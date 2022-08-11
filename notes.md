Index Page:
    Shows user's PSET alloted time schedule + matches of other users in those sessions:
        eg: CS50 PSET session with Adam Zhou on Wednesday 2 pm
    
    This dynamically updates as there's more users registering into the website with ranked choices of class preferences and time slots


SQL Tables

users
    id
    username
    hash (password)
    

course_preferences
    id
    choices
    course_times
    

    
matches
    user_id 
    match_id
    course
    time_matched
    actual_time