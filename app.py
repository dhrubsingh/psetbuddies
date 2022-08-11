import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///psets.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    id = session["user_id"]
    current_user = db.execute("SELECT fullname FROM users WHERE id = ?", id)[0]["fullname"]
    chosen_time = db.execute("SELECT time FROM coursepref WHERE id = ? ", id)[0]["time"].split(",")
    pref = db.execute("SELECT course FROM coursepref WHERE id = ?", id)[0]["course"]

    return render_template("index.html", time=chosen_time, course=pref, current_user=current_user)



@app.route("/availability", methods=["GET", "POST"])
@login_required
def availability():
    if request.method == "GET":
        courses = ["CS50", "EC 10A", "EXPOS 20: 1984", "MATH 1A", "MATH 55A", "LS50", "LS1A", "MATH 21A", "MATH 21B", "MATH 25A", "CS61", "CS 121", "CS 120", "GOV 20", "HUM 10", "PSYCH 1"]
        times = ["8am-9am", "9am-10am", "10am-11am", "11am-12pm", "12pm-1pm", "1pm-2pm", "2pm-3pm", "3pm-4pm", "4pm-5pm", "5pm-6pm", "6pm-7pm", "7pm-8pm", "8pm-9pm",
        "9pm-10pm", "10pm-11pm", "11pm-12pm", "12am-1am", "1am-2am"]
        return render_template("availability.html", courses=courses, times=times)

    else:
        id = session["user_id"]
      
        # collect course preference
        pref = request.form.get("pref")
     
        # collect time preferences
        longtimes = request.form.get("finaltimes")
       
        existing = db.execute("SELECT * from coursepref where id = ?", id)

        if (len(existing) == 0):
            # old:
            db.execute("INSERT INTO coursepref (id, course, time) VALUES (?, ?, ?)", id, pref, longtimes)
        else:
            db.execute("UPDATE coursepref SET id = ?, course = ?, time = ? WHERE id = ?", id, pref, longtimes, id)
   
        user_times = db.execute("SELECT time FROM coursepref WHERE id = ?", id)[0]["time"]
        user_times = user_times.split(",")

        # get all the IDs of users 
        compare_ids = db.execute("SELECT id FROM coursepref WHERE course == ?", pref)
        id_list = []
        for key in compare_ids:
            id_list.append(key["id"])

        # remove current user in session from id_list as we don't want to match user with themselves
        id_list.remove(id)
    
        matches = []

        # matching algorithm
        for utime in user_times:
            for other_id in id_list:
                other_times = db.execute("SELECT time FROM coursepref WHERE id = ?", other_id)[0]["time"].split(",")
    
                for otime in other_times:
                    temp = []
                    if (utime == otime):

                        # get name of match
                        match_name = db.execute("SELECT fullname FROM users WHERE id = ?", other_id)[0]["fullname"]
                        match_contact = db.execute("SELECT contact FROM users WHERE id = ?", other_id)[0]["contact"]
                        db.execute("INSERT INTO matches (user_id, match_id, course, time_matched, actual_time) VALUES (?, ?, ?, ?, ?)", 
                        id, other_id, pref, utime, datetime.now())

                        # Just get matches here into a dict
                        temp = [match_name, utime, match_contact]
                        matches.append(temp)
                    
        chosen_time = db.execute("SELECT time FROM coursepref WHERE id = ? ", id)[0]["time"].split(",")
        current_user = db.execute("SELECT fullname FROM users WHERE id = ?", id)[0]["fullname"]

        return render_template("index.html", time=chosen_time, course=pref, matches=matches, current_user=current_user)


@app.route("/matches")
@login_required
def matches():
    id = session["user_id"]
    history = db.execute("SELECT DISTINCT match_id, course, time_matched, actual_time FROM matches WHERE user_id = ? ", id)

    final_history = []

    for val in history:
        match_temp = db.execute("SELECT fullname FROM users WHERE id = ?", val["match_id"])[0]["fullname"]
        temp = [match_temp, val["course"], val["time_matched"], val["actual_time"]]
        final_history.append(temp)

    print(final_history)

    return render_template("matches.html", history=final_history)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # If POST, check for errors and insert into users table
    if request.method == "POST":
        # get username
        username = request.form.get("username")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        contact = request.form.get("contact")

        confirmation = request.form.get("confirmation")
        existing_users = db.execute("SELECT username FROM users")
     
        # populate all existing usernames into a list for comparison later
        username_database = []
        for user in existing_users:
            username_database.append(user["username"])
        
        # if blank or already exists, render apology
        if (len(username) == 0):
            return apology("Invalid username")
        elif (username in username_database):
            return apology("Username taken")
        
        if (len(password) == 0):
            return apology("Invalid password")
        elif (password != confirmation):
            return apology("Passwords don't match")
            
        # Insert new user into users table
        db.execute("INSERT INTO users (username, fullname, contact, hash) VALUES (?, ?, ?, ?)", username, fullname, contact, generate_password_hash(password))
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)
        print(user_id[0]["id"])
        session["user_id"] = user_id[0]["id"]
        return redirect("/")

    # if GET, display registration form
    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)
    

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
