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

##### Registration
1. Input username  
2. Input password and confirm password
3. Select if you want a simple checklist or extended tracking option  
4. Once registered, user will be redirected tracking interface of their choice

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



