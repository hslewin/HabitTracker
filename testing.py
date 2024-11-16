import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta

app = Flask(__name__)

class HabitTracker:
    def __init__(self):
        self.login_data = pd.read_csv("logins.csv") #all logins for the application, includes username, password, streak, and streak_date
        self.daily_data = pd.read_csv("user_habits.csv") #holding place, will be overwritten during successful login
        self.today = date.today().strftime('%Y-%m-%d')
        self.setting_default = True
        self.username=""
        self.streak=0
        self.streak_date=""
        self.water_oz=0
    
    #method to check in username and password match
    def checkLogin(self, username, password):
        return ((self.login_data['username'] == username) & (self.login_data['password'] == password)).any()

    def check_today_entry(self):
        today_entry = self.daily_data[self.daily_data['Date'] == self.today]
        if not today_entry.empty:
            print("Today's entry exists.")
            return today_entry.iloc
        else:
            print("No entry for today.")
            return None

    def track_habits(self, water_intake=False, exercise_completed=False, exercise_completed2=False, exercise_outside=False, diet_followed=False, read_pages=False, picture_taken=False):
        # Check if there's already an entry for today
        existing_entry = self.daily_data[self.daily_data['Date'] == self.today]
        
        if existing_entry.empty:
            # Create a new entry for today if it doesn't exist
            new_entry = {
                'Date': self.today,
                'Water': water_intake,
                'Exercise': exercise_completed,
                'Exercise2': exercise_completed2,
                'Outside': exercise_outside,
                'Diet': diet_followed,
                'Read': read_pages,
                'Picture': picture_taken,
                'streak_number': 0,  
            }
            self.daily_data = pd.concat([self.daily_data, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            # Update the existing entry
            idx = existing_entry.index[0]
            self.daily_data.at[idx, 'Water'] = water_intake
            self.daily_data.at[idx, 'Exercise'] = exercise_completed
            self.daily_data.at[idx, 'Exercise2'] = exercise_completed2
            self.daily_data.at[idx, 'Outside'] = exercise_outside
            self.daily_data.at[idx, 'Diet'] = diet_followed
            self.daily_data.at[idx, 'Read'] = read_pages
            self.daily_data.at[idx, 'Picture'] = picture_taken

        # Check if all tasks are completed
        self.check_all_tasks_completed(self.today)
        self.update_streak_2()

        # Save updated data to CSV
        self.daily_data.to_csv(f"{self.username}_daily_data.csv", index=False)
        
    def track_habits_extended(self, 
                          water_intake=0, water_oz=0, 
                          exercise_completed=False, e1_time=0, e1_type='', 
                          exercise_completed2=False, e2_time=0, e2_type='', 
                          diet_followed=False, 
                          calories=0, read_pages=0, pages=0, 
                          title='', picture_taken=False, water_oz_extra=0):
        # Check if there's already an entry for today
        existing_entry = self.daily_data[self.daily_data['Date'] == self.today]
        
        if existing_entry.empty:
            # Create a new entry for today if it doesn't exist
            new_entry = {
                'Date': self.today,
                'Water_intake': water_intake or False,
                'Water_oz': water_oz or 0,
                'Exercise_completed': exercise_completed or False,
                'E1_Time': e1_time or 0,
                'E1_Type': e1_type or '',
                'Exercise_completed2': exercise_completed2 or False,
                'E2_Time': e2_time or 0,
                'E2_Type': e2_type or '',
                'Diet_followed': diet_followed or False,
                'Calories': calories or 0 ,
                'Read_pages': read_pages or False,
                'Pages': pages or 0,
                'Title': title or '',
                'Picture_taken': picture_taken or False,
                'Water_oz_extra': water_oz_extra or 0,
                'streak_number': 0,  
            }
            self.daily_data = pd.concat([self.daily_data, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            # Update the existing entry
            idx = existing_entry.index[0]
            self.daily_data.at[idx, 'Water_intake'] = water_intake
            self.daily_data.at[idx,'Water_oz']= water_oz
            self.daily_data.at[idx, 'Exercise_completed'] = exercise_completed
            self.daily_data.at[idx, 'E1_Time'] = e1_time
            self.daily_data.at[idx, 'E1_Type'] = e1_type
            self.daily_data.at[idx, 'Exercise_completed2'] = exercise_completed2
            self.daily_data.at[idx, 'E2_Time'] = e2_time
            self.daily_data.at[idx, 'E2_Type'] = e2_type
            self.daily_data.at[idx, 'Diet_followed'] = diet_followed
            self.daily_data.at[idx,'Calories'] = calories
            self.daily_data.at[idx, 'Read_pages',] = read_pages
            self.daily_data.at[idx, 'Pages'] =  pages
            self.daily_data.at[idx, 'Title'] = title
            self.daily_data.at[idx, 'Picture_taken'] = picture_taken
            self.daily_data.at[idx, 'Water_oz_extra']= water_oz_extra
        
        # Check if all tasks are completed
        self.check_all_tasks_completed(self.today)
        self.update_streak_2()


        # Save updated data to CSV
        self.daily_data.to_csv(f"{self.username}_daily_data.csv", index=False)
             
    def check_all_tasks_completed(self, date_check):
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
        self.daily_data.loc[self.daily_data['Date'] == date_check, 'completed'] = all_tasks_completed
        
        return all_tasks_completed
     
    def check_streak(self):
        yesterday_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.streak_date = self.login_data.loc[self.login_data['username'] == self.username, 'streak_date'].values[0]
        
        if yesterday_str == self.streak_date:
            return True
        elif self.streak_date == self.today:
            return False
        else:
            self.streak = 0
            idx = self.login_data[self.login_data['username'] == self.username].index[0]
            self.login_data.at[idx, 'streak'] = self.streak
            return False
        
    def update_streak(self):
        if (self.check_streak() and self.check_all_tasks_completed(self.today)):
            self.streak += 1
        elif self.check_all_tasks_completed(self.today) and self.check_streak()==False:
            self.streak = 1
        else:
            self.streak = 0

        user_login_data = self.login_data[self.login_data['username'] == self.username]
        if not user_login_data.empty:
            idx = user_login_data.index[0]
            self.login_data.at[idx, 'streak'] = self.streak
            self.login_data.at[idx, 'streak_date'] = self.today
            self.login_data.to_csv("logins.csv", index=False)

        self.daily_data.loc[self.daily_data['Date'] == self.today, 'streak_number'] = self.streak
        self.daily_data.to_csv(f"{self.username}_daily_data.csv", index=False)

    def update_streak_2(self):    
        current_streak=self.calculate_recent_streak()
        print( current_streak)
        
        if self.check_all_tasks_completed(self.today):
            current_streak += 1
        
        if current_streak >0:   
            user_login_data = self.login_data[self.login_data['username'] == self.username]
            if not user_login_data.empty:
                idx = user_login_data.index[0]
                self.login_data.at[idx, 'streak'] = current_streak
                self.login_data.at[idx, 'streak_date'] = self.today
                self.login_data.to_csv("logins.csv", index=False)

            self.daily_data.loc[self.daily_data['Date'] == self.today, 'streak_number'] = current_streak
            self.daily_data.to_csv(f"{self.username}_daily_data.csv", index=False)
            
    def calculate_recent_streak(self):
        # Filter rows where tasks were completed
        completed_dates = self.daily_data[self.daily_data['completed'] == True]['Date']
        
        if completed_dates.empty:
            return 0
        
        # Convert dates to datetime objects and sort in descending order
        dates = pd.to_datetime(completed_dates).sort_values(ascending=False)
        
        if isinstance(self.today, str):
            today = pd.to_datetime(self.today)
        else:
            today= self.today
        
        dates=dates[dates<self.today]
        
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
    return render_template('login.html')

#standard login page
@app.route('/login', methods=["GET", "POST"])
def login():
    error = None 
    if request.method == 'POST':  
        username = request.form['username']
        password = request.form['password']
        if habit_tracker.checkLogin(username, password):
            user_daily = f"{username}_daily_data.csv"  
            habit_tracker.daily_data = pd.read_csv(user_daily)
            habit_tracker.username=username
            habit_tracker.streak = int(habit_tracker.login_data.loc[habit_tracker.login_data['username']== habit_tracker.username, 'streak'].values[0] )
            habit_tracker.streak_date = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'streak_date'].values[0]
            habit_tracker.setting_default = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'default_tracking'].values[0]
            return redirect(url_for('tracker_redirect'))  
        else:
            error = "Login failed. Try again. Or sign-up for an account"
   
    return render_template('login.html', error=error)

#logout page
@app.route('/logout')
def logout():
    # Reset habit_tracker data
    habit_tracker.daily_data = pd.DataFrame()  # Empty DataFrame
    habit_tracker.username = ""
    habit_tracker.streak = 0
    habit_tracker.streak_date = ''
    habit_tracker.setting_default = ''
    habit_tracker.water_oz=0
    
    return redirect(url_for('login'))  # Redirect to login page

#registration page
@app.route('/register', methods=["GET", "POST"])
def register():
    error = None
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
                    daily_data_df = pd.DataFrame(columns=['Date', 'Water', 'Exercise', 'Exercise2', 'Outside', 'Diet', 'Read', 'Picture', 'completed', 'streak_number'])
                else:
                    daily_data_df = pd.DataFrame(columns=['Date', 'Water','Water_oz','Exercise','Exercise2','Outside','Diet','Read','Picture','completed','streak_number','Water_Oz','E1_Time','E1_Type','E2_Time','E2_Type','Calories','Pages','Title'])
                
                daily_data_df.to_csv(user_daily_file, index=False)

                return redirect(url_for('login'))

    return render_template('register.html', error=error)

#redirect page to deterime which checklist page will be displayed
@app.route('/tracker_redirect')
def tracker_redirect():
    if  habit_tracker.setting_default == True:
            return redirect(url_for('tracker_default'))
    else:
        return redirect(url_for('tracker_extra')) 

@app.route('/tracker_default', methods=['GET', 'POST'])
def tracker_default():
    today_entry = habit_tracker.daily_data[habit_tracker.daily_data['Date'] == habit_tracker.today]
    
    if request.method == 'POST':
        water_intake = 'water_intake' in request.form
        exercise_completed = 'exercise_completed' in request.form
        exercise_completed2 = 'exercise_completed2' in request.form
        exercise_outside = 'exercise_outside' in request.form
        diet_followed = 'diet_followed' in request.form
        read_pages = 'read_pages' in request.form
        picture_taken = 'picture_taken' in request.form
        
        habit_tracker.track_habits(water_intake, exercise_completed, exercise_completed2, exercise_outside, diet_followed, read_pages, picture_taken)
        return redirect(url_for('tracker_default'))
    
    # Set default values if today_entry is empty
    if today_entry.empty:
        today_entry_data = {
            'Water': False,
            'Exercise': False,
            'Exercise2': False,
            'Outside': False,
            'Diet': False,
            'Read': False,
            'Picture': False
        }
    else:
        today_entry_data = today_entry.iloc[0].to_dict()
    
    return render_template('tracker_default.html', daily_data=today_entry_data, streak=habit_tracker.streak)

@app.route('/tracker_extra', methods=['GET', 'POST'])
def tracker_extra():
    today_entry = habit_tracker.daily_data[habit_tracker.daily_data['Date'] == habit_tracker.today]
    
    if request.method == 'POST':
        water_intake = 'Water_intake' in request.form
        water_oz_str = request.form.get('Water_oz', '0')
        water_oz = int(water_oz_str) if water_oz_str.isdigit() else 0
        
        water_oz_extra_str = request.form.get('Water_oz_extra', '0')
        water_oz_extra = int(water_oz_extra_str) if water_oz_extra_str.isdigit() else 0
        water_oz += water_oz_extra
        habit_tracker.water_oz = water_oz
        
        exercise_completed = 'Exercise_completed' in request.form
        e1_time_str = request.form.get('E1_Time', '0')
        e1_time = int(e1_time_str) if e1_time_str.isdigit() else 0
        e1_type = request.form.get('E1_Type', "")
        
        exercise_completed2 = 'Exercise_completed2' in request.form
        e2_time_str = request.form.get('E2_Time', '0')
        e2_time = int(e2_time_str) if e2_time_str.isdigit() else 0
        e2_type = request.form.get('E2_Type', "")
        
        diet_followed = 'Diet_followed' in request.form
        calories_str = request.form.get('Calories', '0')
        calories = int(calories_str) if calories_str.isdigit() else 0
        
        read_pages = 'Read_pages' in request.form
        title = request.form.get('Title', "")  
        
        pages_str = request.form.get('Pages', '0')
        pages = int(pages_str) if pages_str.isdigit() else 0
        if pages >= 10:
            read_pages = True
        
        picture_taken = 'Picture_taken' in request.form

        habit_tracker.track_habits_extended(water_intake, water_oz, exercise_completed, e1_time, e1_type, exercise_completed2, e2_time, e2_type, diet_followed, calories, read_pages, pages, title, picture_taken, water_oz_extra)
        return redirect(url_for('tracker_extra'))
    
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
            'E1_Time': 0,
            'E1_Type': '',
            'E2_Time': 0,
            'E2_Type': '',
            'Calories': 0,
            'Pages': 0,
            'Title': '',
            'Water_oz_extra': 0,
        }
    else:
        today_entry_data = today_entry.iloc[0].to_dict()

    return render_template('tracker_extra.html', daily_data=today_entry_data, streak=habit_tracker.streak, water_num=habit_tracker.water_oz)



if __name__ == '__main__':
    app.run(debug=True)



