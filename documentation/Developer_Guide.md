# Guide for Developers

## Project Overview

### 75 Hard Challenge
The tracker is based on the 75 Hard Challenge.
There are multiple goals to achieve each day or the challenge resets.

Goals:
- Drink 1 gallon (128 ounces) of water
- Exercise 45 minutes outside
- Exercise an additional 45 minutes
- Follow a diet of your choosing, no alchol allowed, no cheat days
- Read 10 pages of a non-fiction book
- Take a progress photo everyday
  
### Application Developement Componenets

#### Mechanisms
- Flask: Python web framework for building applications 
- Data: Habit data will be stored locally in a CSV file. 

#### GUI 
- The app will have a simple flask based GUI to provide users with an intuitive visual interface
- Graphs will be added to visualize progress over time

#### User Activity Flow
##### Sign-in
1. Input username and password to login and be directed to the user's tracking interface of choice  
   Alternatively link to a registration page if user doesn't have a username and password yet
<img src= https://github.com/hslewin/HabitTracker/blob/main/documentation/HT_Login.png alt="Login Page" width=75% height=auto>

##### Registration
1. Input username  
2. Input password and confirm password
3. Select if you want a simple checklist or extended tracking option  
4. Once registered, user will be redirected tracking interface of their choice

<img src= https://github.com/hslewin/HabitTracker/blob/main/documentation/HT_reg.png alt="Registration Page" width=75% height=auto>

##### Default Tracker (simple checklist)
1. Checkbox for each of the goals
- Drink 1 gallon (128 ounces) of water
- Exercise 45 minutes outside
- Exercise an additional 45 minutes
- Follow a diet of your choosing, no alchol allowed, no cheat days
- Read 10 pages of a non-fiction book
- Take a progress photo everyday
2. Submit data button, user will redirected back to this tracker with checkbox data retained/visualized
3. Over challenge progreess and daily progress visuallizations on the right half of the page
4. User can logout when finished

<img src= https://github.com/hslewin/HabitTracker/blob/main/documentation/HT_default.png alt="Default Tracker Page" width=75% height=auto>

##### Extended Tracker (extended tracking)
1. Checkbox with expandable area for each of the goals
- Drink 1 gallon (128 ounces) of water
  --three buttons for added set amounts of water
  --one input box for adding various amounts of water
- Exercise 45 minutes outside
  -- Input for type of exercise
  -- Input for amount of time spent
- Exercise an additional 45 minutes
  -- Input for type of exercise
  -- Input for amount of time spent
- Follow a diet of your choosing, no alchol allowed, no cheat days
  -- Input for number of Calories
- Read 10 pages of a non-fiction book
  -- Input for title of book
  -- Input for number of pages read
- Take a progress photo everyday (does not include expandable area)
2. Submit data button, user will redirected back to this tracker with checkbox data retained/visualized
3. Over challenge progreess and daily progress visuallizations on the right half of the page
4. When goal's expandable area is opened the numerical data for the goal is displayed as well
5. User can logout when finished

<img src= https://github.com/hslewin/HabitTracker/blob/main/documentation/HT_extended.png alt="Extended Tracker Page" width=75% height=auto>

#### Key Application Elements
##### Templates
There are four html templates for the login, registration, default tracker, and extended tracker pages.
- The login and registration pages are simple input boxes and submit buttons for the most part. There are built-in redirects back and forth between these pages.
- The default tracker is a form with simple checkboxes and two displays run by fairly straighforward scripts. One display tracks the number of days completed. The other tracks progress towards todays completion.
- The extended tracker contains all of the elements of the default tracker with addtional expanding areas to allow users to track more data if that is desired. There are functions to track and display water and calories. There are togglable sections available for 5 of the 6 goals. When a goal is toggled open the extra entry fields become availble, the associated graph is displayed, and an indication arrow is shifted.
##### Static and Style  
The static folder only contains the style sheet for the application. 
The code in the toggleable sections is dependent on aspect of the style sheet, which enable parts of the page to be hidden and reveald as desired
##### Necessary CSV files
- logins.csv is needed to be able to login to the application &/or create new users
- User_habits.csv is the template for user's daily data and is required for the applicaiton to function properly
##### App.py
This is the main page for the application. It contains both the class developed for the project and the flask framework that support the html pages.
###### HabitTracker Class
None of the functions would be available to end users, The functions could be simplified in the future
- checkLogin: Checks to see if the username and password are both correct
- check_today_entry: Check if there is a current entry in the user's daily data for the current day
- track_habits: Saving data for the various goals of the "challenge", simple checklist,
  -- functions used: check_all_tasks_completed, update_streak
- track_habits_extended: Saving data for the various goals of the "challenge", extended with extra data
  -- functions used: check_all_tasks_completed, update_streak
- check_all_tasks_complete: Check if all the daily goals have been achieved.
- update_streak: Updates the streak date and count 
  -- functions used: check_all_tasks_complete, calulate_recent_streak
- calculate_recent_streak: Calculate the number of consecutive previous days in which all tasks were completed
###### Flask pages
- home:
  -- redirects to 'login' 
- login: pulls data from imputs, checkLogin, added user data to the session
  -- redirects to a 'tracker_redirect' 
- logout: clears all user data from the session
  -- redirects to 'login' page
- register: pulls data from inputs, sets up user data for the session
  -- redirects to 'tracker_redirect'
- tracker_redirect: determines which version of the tracker to redirect the user based on their version selection
  -- redirects to either 'tracker_default' or 'tracker_extended'
- tracker_default: pulls data from inputs and saves
  -- redirects to self, 'tracker_default', with data pulled forward
- tracker_extended: pulls data from inputs and saves, creates graphs for page
  -- redirects to self, 'tracker_extended', with data pulled forward

#### Possible Future Work
- Customization: I would have liked to have a fully customizable checklist that is determined by the user. This would require a reworking of quite a bit of the code and some of the structure.
- User settings: I would like to have a user settings page so that selections could be adjusted to meet the user's changing preferences
- Better Security: I don't have experience in security so didn't implement any security and very minimal error catching
- Better visuals: While the visuals are okay, there are many elements that are very rough and need finessing. Function was prioritized over form. 

