import os
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta

app = Flask(__name__)

class HabitTracker:
    def __init__(self):
        self.login_data = pd.read_csv("logins.csv") #all logins for the application, includes username, password, default_tracking, streak, and streak_date
        self.daily_data = pd.read_csv("user_habits.csv") #holding place, will be overwritten during successful login
        self.today = date.today().strftime('%Y-%m-%d')
        self.setting_default = True
        self.username=""
        self.streak=0
        self.streak_date=""
        self.water_oz=0
        self.cal=0
    
    #method to check in username and password match
    def checkLogin(self, username, password):
        '''Checks to see if the username and password are both correct
        Args:
            username: user's identification, must be string
            password: password associated with user, must be string
        
        Returns: boolean true if user name and password match entries, false if there is both don't match
        '''
        return ((self.login_data['username'] == username) & (self.login_data['password'] == password)).any()

    def check_today_entry(self):
        '''Checks if there is a current entry in the user's daily data for the current day.
        
        Returns: if there is an entry will return the entry index, otherwise returns none
        '''
        #Check if entry for today's date exists
        today_entry = self.daily_data[self.daily_data['Date'] == self.today]
        if not today_entry.empty:
            return today_entry.iloc
        else:
            return None

    def track_habits(self, water_intake=False, exercise_completed=False, exercise_completed2=False, diet_followed=False, read_pages=False, picture_taken=False):
        '''Saving data for the various goals of the "challenge", simple checklist
        
        Args: 
            water_intake: did the user complete water intake for the day, pulled from checkbutton, must be boolean, defalult=False
            exercise_completed: did the user complete exercise 1 for the day, pulled from checkbutton, must be boolean, defalult=False
            exercise_completed2: did the user complete exercise 2 for the day, pulled from checkbutton, must be boolean, defalult=False
            diet_followed: did the user follow the diet for the day, pulled from checkbutton, must be boolean, defalult=False
            read_pages: did the user read set pages for the day, pulled from checkbutton, must be boolean, defalult=False
            picture_taken: did the user take a picture for the day, pulled from checkbutton, must be boolean, defalult=False
        
        Returns: no return, data is saved to user's daily_data.csv
        '''
        # Check if there's already an entry for today
        existing_entry = self.daily_data[self.daily_data['Date'] == self.today]
        
        if existing_entry.empty:
            # Create a new entry for today if it doesn't exist
            new_entry = {
                'Date': self.today,
                'Water_intake': water_intake,
                'Exercise_completed': exercise_completed,
                'Exercise_completed2': exercise_completed2,
                'Diet_followed': diet_followed,
                'Read_pages': read_pages,
                'Picture_taken': picture_taken,
                'Day_completed': False,
                'Streak_number': 0,  
            }
            self.daily_data = pd.concat([self.daily_data, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            # Update the existing entry
            idx = existing_entry.index[0]
            self.daily_data.at[idx, 'Water_intake'] = water_intake
            self.daily_data.at[idx, 'Exercise_completed'] = exercise_completed
            self.daily_data.at[idx, 'Exercise_completed2'] = exercise_completed2
            self.daily_data.at[idx, 'Diet_followed'] = diet_followed
            self.daily_data.at[idx, 'Read_pages'] = read_pages
            self.daily_data.at[idx, 'Picture_taken'] = picture_taken

        # Check if all tasks are completed
        self.check_all_tasks_completed(self.today)
        self.update_streak()

        # Save updated data to CSV
        self.daily_data.to_csv(f"{self.username}_daily_data.csv", index=False)
        
    def track_habits_extended(self, 
                          water_intake=False, water_oz=0, water_oz_extra=0,
                          exercise_completed=False, e1_time=0, e1_type='', 
                          exercise_completed2=False, e2_time=0, e2_type='', 
                          diet_followed=False, calories=0, 
                          read_pages=False, pages=0, title='', 
                          picture_taken=False ):        
        '''Saving data for the various goals of the "challenge", extended with extra data
        
        Args: 
            water_intake: did the user complete water intake for the day, pulled from checkbutton, must be boolean, defalult=False,
            water_oz: number of overall ounces consumed for the day, must be int, default=0, 
            water_oz_extra: number of ounces consumed before added to the total, must be int, default=0,
            exercise_completed: did the user complete exercise 1 for the day, pulled from checkbutton, must be boolean, defalult=False,
            e1_time: number of minutes exercised outside, must be int, default=0, 
            e1_type: type of exercise completed, must be a string, default='', 
            exercise_completed2: did the user complete exercise 2 for the day, pulled from checkbutton, must be boolean, defalult=False,
            e2_time: number of minutes exercised in second session, must be int, default=0, 
            e2_type: type of exercise completed, must be a string, default='',
            diet_followed: did the user follow the diet for the day, pulled from checkbutton, must be boolean, defalult=False,
            calories: number of calories ingetested, must be int, default=0, 
            read_pages: did the user read set pages for the day, pulled from checkbutton, must be boolean, defalult=False
            pages: nubmer of pages read, must be int, default=0, 
            title: title of the book that is read, must be string, default='',
            picture_taken: did the user take a picture for the day, pulled from checkbutton, must be boolean, defalult=False
        
        Returns: no return, data is saved to user's daily_data.csv
        '''
        # Check if there's already an entry for today, save to local variable
        existing_entry = self.daily_data[self.daily_data['Date'] == self.today]
        
        #Add water ounce, check if meet the daily goal, if meet change checkbox to true
        self.water_oz = water_oz
        water_oz += water_oz_extra
        if water_oz >= 128:
            water_intake = True
        
        #check if exercise 1 meets daily goal, if meet change checkbox to true
        if e1_time >= 45:
            exercise_completed = True
    
        #check if exercise 2 meets daily goal, if meet change checkbox to true
        if e2_time >= 45:
            exercise_completed2 = True
        
        #check if pages read meets daily goal, if meet change checkbox to true
        if pages >=10:
            read_pages = True
        
        #add calories in input to running total of calories,
        self.cal +=calories
        calories=self.cal
        
        if existing_entry.empty:
            # Create a new entry for today if it doesn't exist
            new_entry = {
                'Date': self.today,
                'Water_intake': water_intake or False,
                'Water_oz': water_oz or 0,
                'Exercise_completed': exercise_completed or False,
                'E1_time': e1_time or 0,
                'E1_type': e1_type or '',
                'Exercise_completed2': exercise_completed2 or False,
                'E2_time': e2_time or 0,
                'E2_type': e2_type or '',
                'Diet_followed': diet_followed or False,
                'Calories': calories or 0 ,
                'Read_pages': read_pages or False,
                'Pages': pages or 0,
                'Title': title or '',
                'Picture_taken': picture_taken or False,
                'Day_completed': False,
                'Streak_number': 0,  
            }
            self.daily_data = pd.concat([self.daily_data, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            # Update the existing entry
            idx = existing_entry.index[0]
            self.daily_data.at[idx, 'Water_intake'] = water_intake
            self.daily_data.at[idx,'Water_oz']= water_oz 
            self.daily_data.at[idx, 'Exercise_completed'] = exercise_completed
            self.daily_data.at[idx, 'E1_time'] = e1_time
            self.daily_data.at[idx, 'E1_type'] = e1_type
            self.daily_data.at[idx, 'Exercise_completed2'] = exercise_completed2
            self.daily_data.at[idx, 'E2_time'] = e2_time
            self.daily_data.at[idx, 'E2_type'] = e2_type
            self.daily_data.at[idx, 'Diet_followed'] = diet_followed
            self.daily_data.at[idx, 'Calories'] = calories
            self.daily_data.at[idx, 'Read_pages',] = read_pages
            self.daily_data.at[idx, 'Pages'] =  pages
            self.daily_data.at[idx, 'Title'] = title
            self.daily_data.at[idx, 'Picture_taken'] = picture_taken
        
        # Check if all tasks are completed
        self.check_all_tasks_completed(self.today)
        self.update_streak()

        # Save updated data to CSV
        self.daily_data.to_csv(f"{self.username}_daily_data.csv", index=False)
             
    def check_all_tasks_completed(self, date_check):
        '''Checks if all the daily goals have been achieved.
        
        Args: 
            date_check: the entry date to be checked, must be '%Y-%m-%d' string
        
        Returns: true if all tasks are completed (true), false if any are missing 
        
        '''
        # Get today's entry
        if self.daily_data[self.daily_data['Date'] == date_check].empty:
            return False  # Return False if there's no entry for the given date

        check_entry = self.daily_data[self.daily_data['Date'] == date_check].iloc[0]
        
        # List of tasks to check
        tasks = ['Water_intake', 'Exercise_completed', 'Exercise_completed2', 'Diet_followed', 'Read_pages', 'Picture_taken']

        # Iterate through each task to see if it's completed
        all_tasks_completed = True  # Assume all tasks are completed
        for task in tasks:
            if not bool(check_entry[task]):  # Convert the value to boolean
                all_tasks_completed = False  # If any task is incomplete, set to False
                break  # Exit the loop early if any task is incomplete

        # Mark the day as completed or not
        self.daily_data.loc[self.daily_data['Date'] == date_check, 'Day_completed'] = all_tasks_completed
        
        return all_tasks_completed
            
    def update_streak(self):    
        '''Updates the streak date and count 
        
        Returns: no return, updates app attributes and saves data to csv      
        '''
        #calculate the current streak 
        current_streak=self.calculate_recent_streak()
            
        #check if today's streak has been completed
        if self.check_all_tasks_completed(self.today):
            current_streak += 1
        
        #if streak is larger that 0 update the streak information in the app data and the csv
        if current_streak >0:   
            user_login_data = self.login_data[self.login_data['username'] == self.username]
            if not user_login_data.empty:
                idx = user_login_data.index[0]
                self.login_data.at[idx, 'streak'] = current_streak
                self.login_data.at[idx, 'streak_date'] = self.today
                self.login_data.to_csv("logins.csv", index=False)

            self.daily_data.loc[self.daily_data['Date'] == self.today, 'Streak_number'] = current_streak
            self.daily_data.to_csv(f"{self.username}_daily_data.csv", index=False)
            
    def calculate_recent_streak(self):
        '''Calculate the number of consecutive previous days in which all tasks were completed
        
        Return: the number of days, must be int
        '''
        # Filter rows where tasks were completed
        completed_dates = self.daily_data[self.daily_data['Day_completed'] == True]['Date']
        
        if completed_dates.empty:
            return 0
        
        # Convert dates to datetime objects and sort in descending order
        dates = pd.to_datetime(completed_dates).sort_values(ascending=False)
        
        if isinstance(self.today, str):
            today = pd.to_datetime(self.today)
        else:
            today= self.today
        
        dates=dates[dates<self.today]
        
        #if today is first streak date
        if dates.empty:
            return 0
        
        # Check if the most recent completion was yesterday
        if dates.iloc[0] != today - timedelta(days=1):
            return 0  # No streak if yesterday was not completed
        
        streak = 0
        
        for i in range(1, len(dates)):
            if dates.iloc[i-1] - dates.iloc[i] == timedelta(days=1):
                streak += 1
            else:
                break
        
        return streak

habit_tracker = HabitTracker()


@app.route('/')
def home():
    '''
    Handles redirecting to the login page
    
    '''
    return render_template('login.html')

#standard login page
@app.route('/login', methods=["GET", "POST"])
def login():
    '''
    Handles user login
    
    Request Body:
        username: username of the user, string
        password: user's password, string
    
    Return:
        error: if login fails
    '''
    
    error = None 
    #request block
    if request.method == 'POST':  
        username = request.form['username']
        password = request.form['password']
        
        #check username and password, save info into application session, redirect to redirecting page
        if habit_tracker.checkLogin(username, password):
            user_daily = f"{username}_daily_data.csv"  
            habit_tracker.daily_data = pd.read_csv(user_daily)
            habit_tracker.username=username
            habit_tracker.streak = int(habit_tracker.login_data.loc[habit_tracker.login_data['username']== habit_tracker.username, 'streak'].values[0] )
            habit_tracker.streak_date = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'streak_date'].values[0]
            habit_tracker.setting_default = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'default_tracking'].values[0]
            return redirect(url_for('tracker_redirect'))  
        
        #if not correct username and password, present error message
        else:
            error = "Login failed. Try again. Or sign-up for an account"
   
    return render_template('login.html', error=error)

#logout page
@app.route('/logout')
def logout():
    '''
    Handles user logout, clears the saved session data
    '''
    # Reset habit_tracker data
    habit_tracker.daily_data = pd.DataFrame()  # Empty DataFrame
    habit_tracker.username = ""
    habit_tracker.streak = 0
    habit_tracker.streak_date = ''
    habit_tracker.setting_default = ''
    habit_tracker.water_oz=0
    habit_tracker.cal=0
    
    return redirect(url_for('login'))  # Redirect to login page

#registration page
@app.route('/register', methods=["GET", "POST"])
def register():
    '''
    Handles user registration
    
    Request Body:
    username: username of the user, string
    password: user's password, string
    confirm_password: user's second version of their password, string
    default_tracking: selection choice of version of tracker, simple or extended, Boolean: true is simple, false is extended
    
    '''
    error = None
    #request block
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        default_tracking = request.form['default_tracking']

        # Check if passwords match
        if password != confirm_password:
            error = "Passwords do not match."
        else:
            # Load the logins.csv file to check for existing usernames
            df = pd.read_csv("logins.csv")

            # Check if username already exists
            if username in df['username'].values:
                error = "Username already exists. Please choose a different username."
            else:
                # Prepare the new user data as a DataFrame
                new_user = pd.DataFrame({
                    'username': [username],
                    'password': [password],
                    'default_tracking': [default_tracking],
                    'streak': [0],
                    'streak_date': ['']
                })

                # Append the new user data to the CSV without overwriting
                new_user.to_csv("logins.csv", mode='a', header=False, index=False)

                # Refresh login data in the habit tracker instance
                habit_tracker.login_data = pd.read_csv("logins.csv")

                # Create a daily_data.csv file for the user
                user_daily_file = f"{username}_daily_data.csv"
                if default_tracking == True:
                    daily_data_df = pd.DataFrame(columns=['Date', 'Water', 'Exercise', 'Exercise2', 'Outside', 'Diet', 'Read', 'Picture', 'Day_completed', 'Streak_number'])
                else:
                    daily_data_df = pd.DataFrame(columns=['Date', 'Water','Water_oz','Exercise','Exercise2','Outside','Diet','Read','Picture','Day_completed','Streak_number','Water_Oz','E1_time','E1_type','E2_time','E2_type','Calories','Pages','Title'])
                
                daily_data_df.to_csv(f"{user_daily_file}", index=False)
               
                habit_tracker.daily_data = daily_data_df
                habit_tracker.username=username
                habit_tracker.streak = int(habit_tracker.login_data.loc[habit_tracker.login_data['username']== habit_tracker.username, 'streak'].values[0] )
                habit_tracker.streak_date = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'streak_date'].values[0]
                habit_tracker.setting_default = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'default_tracking'].values[0]

                return redirect(url_for('tracker_redirect'))

    return render_template('register.html', error=error)

#redirect page to deterime which checklist page will be displayed
@app.route('/tracker_redirect')
def tracker_redirect():
    '''
    Handles the redirect between the various tracker settings.
    
    '''
    if  habit_tracker.setting_default == True:
            return redirect(url_for('tracker_default'))
    else:
        return redirect(url_for('tracker_extended')) 

#default tracker, simple checklist
@app.route('/tracker_default', methods=['GET', 'POST'])
def tracker_default():
    '''
    Handles the display of the simple checkbox tracker
    
    Request Body:
        water_intake: did the user drink the goal amount of water, boolean  
        exercise_completed: did the user do 45 minutes of outdoor exercise, boolean  
        exercise_completed2: did the user do an additional 45 minutes of exercise, boolean
        diet_followed: did the user follow their diet (no alcohol either), boolean
        read_pages: did the user read at least 10 pages of non-fiction, boolean
        picture_take: did the user take a progress picture, boolean
    '''
    today_entry = habit_tracker.daily_data[habit_tracker.daily_data['Date'] == habit_tracker.today]
    
    #request block
    if request.method == 'POST':
        water_intake = 'Water_intake' in request.form
        exercise_completed = 'Exercise_completed' in request.form
        exercise_completed2 = 'Exercise_completed2' in request.form
        diet_followed = 'Diet_followed' in request.form
        read_pages = 'Read_pages' in request.form
        picture_taken = 'Picture_taken' in request.form
        
        habit_tracker.track_habits(water_intake, exercise_completed, exercise_completed2, diet_followed, read_pages, picture_taken)
        return redirect(url_for('tracker_default'))
    
    # Set default values if today_entry is empty
    if today_entry.empty:
        today_entry_data = {
            'Water_intake': False,
            'Exercise_completed': False,
            'Exercise_completed2': False,
            'Diet_followed': False,
            'Read_pages': False,
            'Picture_taken': False,
            'Day_completed': False
        }
        
    #set values of data to today_entry, information will be passed forward 
    else:
        today_entry_data = today_entry.iloc[0].to_dict()
    
    return render_template('tracker_default.html', daily_data=today_entry_data, streak=habit_tracker.streak)

#extended tracker, extended data and displays
@app.route('/tracker_extended', methods=['GET', 'POST'])
def tracker_extended():
    '''
    Handles the display of the extended tracker with extra data
    
    Request Body:
        water_intake: did the user drink the goal amount of water, boolean  
        water_oz_str: ounces of water inputed via buttons, int
        water_oz_extra_str: ounces of water inputed via input box, int
        exercise_completed: did the user do 45 minutes of outdoor exercise, boolean 
        e1_time_str: minutes exercised outside, int
        e1_type: type of excercise, string
        exercise_completed2: did the user do an additional 45 minutes of exercise, boolean
        e2_time_str: minutes exercised, int
        e2_type: type of excercise, string
        diet_followed: did the user follow their diet (no alcohol either), boolean
        calories_str: number of calories, int
        read_pages: did the user read at least 10 pages of non-fiction, boolean
        title: title of the reading material, string
        pages_str: number of pages read, int
        picture_take: did the user take a progress picture, boolean
    '''
    
    today_entry = habit_tracker.daily_data[habit_tracker.daily_data['Date'] == habit_tracker.today]
    
    #request block
    if request.method == 'POST':
        water_intake = 'Water_intake' in request.form
        water_oz_str = request.form.get('Water_oz', '0')
        water_oz = int(water_oz_str) if water_oz_str.isdigit() else 0
        
        water_oz_extra_str = request.form.get('Water_oz_extra', '0')
        water_oz_extra = int(water_oz_extra_str) if water_oz_extra_str.isdigit() else 0
        
        exercise_completed = 'Exercise_completed' in request.form
        e1_time_str = request.form.get('E1_time', '0')
        e1_time = int(e1_time_str) if e1_time_str.isdigit() else 0
        e1_type = request.form.get('E1_type', "")
        
        exercise_completed2 = 'Exercise_completed2' in request.form
        e2_time_str = request.form.get('E2_time', '0')
        e2_time = int(e2_time_str) if e2_time_str.isdigit() else 0
        e2_type = request.form.get('E2_type', "")
        
        diet_followed = 'Diet_followed' in request.form
        calories_str = request.form.get('Calories', '0')
        calories = int(calories_str) if calories_str.isdigit() else 0
        
        read_pages = 'Read_pages' in request.form
        title = request.form.get('Title', "")  
        
        pages_str = request.form.get('Pages', '0')
        pages = int(pages_str) if pages_str.isdigit() else 0
        
        picture_taken = 'Picture_taken' in request.form

        habit_tracker.track_habits_extended(water_intake, water_oz, water_oz_extra,
                          exercise_completed, e1_time, e1_type, 
                          exercise_completed2, e2_time, e2_type, 
                          diet_followed, calories, 
                          read_pages, pages, title, 
                          picture_taken)
                              
        return redirect(url_for('tracker_extended'))
    
    # Set default values if today_entry is empty
    if today_entry.empty:
        today_entry_data = {
            'Water_intake': False,
            'Exercise_completed': False,
            'Exercise_completed2': False,
            'Diet_followed': False,
            'Read_pages': False,
            'Picture_taken': False,
            'Water_oz': 0,
            'E1_time': 0,
            'E1_type': '',
            'E2_time': 0,
            'E2_type': '',
            'Calories': 0,
            'Pages': 0,
            'Title': '',
            'Water_oz_extra': 0,
            'Cal_extra': 0,
            'Day_completed': False,
        }
    else:
        today_entry_data = today_entry.iloc[0].to_dict()
        
    #graphs to track data for displays on page, data over the course of the challenge
    water = px.line(habit_tracker.daily_data, x='Date', y='Water_oz', title='Water Intake Per Day')
    water_oz_data = water.to_html(full_html=False)
    
    e1 = px.line(habit_tracker.daily_data, x='Date', y='E1_time', title='Outdoor Exercise Per Day')
    e1_time_data= e1.to_html(full_html=False)
    
    e2 = px.line(habit_tracker.daily_data, x='Date', y='E2_time', title='Second Exercise Per Day')
    e2_time_data= e2.to_html(full_html=False)
    
    cal = px.line(habit_tracker.daily_data, x='Date', y='Calories', title='Calories Per Day')
    calories_data= cal.to_html(full_html=False)
    
    pag = px.line(habit_tracker.daily_data, x='Date', y='Pages', title='Pages Read Per Day')
    pages_data = pag.to_html(full_html=False)
    
    return render_template('tracker_extended.html', daily_data = today_entry_data, streak = habit_tracker.streak, water_num = habit_tracker.water_oz, water_oz_data = water_oz_data, e1_time_data = e1_time_data, e2_time_data = e2_time_data, calories_data = calories_data, cal_num = habit_tracker.cal, pages_data= pages_data)

if __name__ == '__main__':
    app.run(debug=True)