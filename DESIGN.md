My project essentially uses the standard CS50 web development stack of a sqlite database, flask backend, and bootstrap CSS and vanilla javascript
front-end. I decided to use this stack as I was already most comfortable with it from doing PSETS in the class.

In terms of the actual implementation of the project, I decided to have three main databases: users.db, coursepref.db, and matches.db to be able to store all the data that I needed for the website. users.db is the standard user information database that stores a user's login details, full name, and contact information (which is useful when I have to identifiy user matches later on). coursepref.db stores each course preference that a user has and the time(s) that they selected.

For the design of the coursepref.db, I chose very strategically to have each user only have one row of entry in this database, and any subsequent entries of the form in the availability page to simply update this database. This is because this made the task of finding the relevant user data and updating the matching algorithm much easier, because I did not have to constantly filter through the SQL table to find the most recent submission to get these preferences. matches.db just stores all the matches the user has had since they created an account in the website, which I thought would be useful in case they wanted to reach out to previous matches that they had while using the service.

One of the most challenging techincal problems that arose for me was trying to implement a ranked choice preference and custom time preference input for courses. Initially, for my project I had created a way to rank the top 3 preferences for the course site. This turned out to be very complicated when I had to match people using an algorithm, because not only did I have to account for the different ranked choice for courses, but to match their custom availability slots with each other too. It was difficult to come up with a way to match someone, for example, who was free from 3-4 pm and someone who was free from 3:30-4:30 pm for 3:30-4pm. To solve this problem, I decided to simplify this by having the user only choose one course and then to have a select option that displays a list of times throughout the day. This made the matching much easier as I could now just check if the users had the exact same time preferences and then consequtively match them.

Another challenging techincal problem that arose for me was then to be able to collect all the data from the time select elements (which is generated dynamically using javascript) and then sending this data to the flask server. This problem was extremely difficult to solve as I had to think about ways to change the GET/POST requests and ways to be able to input the URL form and retreive it using flask but this simply did not work. I also couldn't just request.form.get() all the selects because request.form.get() does not work like javascript's document.querySelector() function. To get around this problem, I basically created an invisible input, called "finaltimes" that basically holds, as its value, the addition of all the available times from the select options. I then used CSS to make this input invisible and get its data using flask, and hence am able to retreive the multiple time availabilities via this way. 

One other problem arose that finaltimes wasn't updating the accurate information because it kept on appending the default select option of 8am-9am in every single entry. I realized this was because I wasn't updating the javascript holding its value whenever I'd add a new time slot and hence submitted the form wihtout updating this. To fix this problem, I had to create the "update" button whose sole purpose is to ensure that "finaltimes" is accurately reflcting the user's input times and is also why I make it imperative that the user clicks update everytime before submitting the form.

Finally, my matching algorithm works as follows: first, go through each available time the user has inputted, then goes through each other user in the system who has a matching course preference to the current user. Then it goes through each of said matching user's availabe free times and compares the matching user's time and the current user's time preference. If these two times match, then the algorithm identifies this as a match and inserts an entry into the matches.db file and adds it into the matches list. After this algorithm runs, the matches list is then passed into the index.html where I use Jinja to then process the data on the webpage. Initially, I had decided to use a dictionary to store this data for matches, but then parsing it was difficult with Jinja because I could only essentially have a single key-value pair. But I decided to use a list of lists instead, where every list within the list has different indexes reflecting a different data point about the match: which in this case is the match name, time they matched, and the contact information of the match. 