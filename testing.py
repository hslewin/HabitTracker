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
        self.setting_default = 'default'
        self.username=""
        self.streak=0
        self.streak_date=""
    
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

    def track_habits(self, water_intake, exercise_completed, exercise_completed2, exercise_outside, diet_followed, read_pages, picture_taken):
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
     
         
    def check_all_tasks_completed(self, date_check):
        # Get today's entry
        if self.daily_data[self.daily_data['Date'] == date_check].empty:
            return False  # Return False if there's no entry for the given date

        check_entry = self.daily_data[self.daily_data['Date'] == date_check].iloc[0]
        
        # List of tasks to check
        tasks = ['Water', 'Exercise', 'Exercise2', 'Outside', 'Diet', 'Read', 'Picture']

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
        
    
    def calculate_recent_streak(self):
        # Filter rows where tasks were completed
        completed_dates = self.daily_data[self.daily_data['completed'] == True]['Date']
        
        if completed_dates.empty:
            return 0
        
        # Convert dates to datetime objects and sort in descending order
        dates = pd.to_datetime(completed_dates).sort_values(ascending=False)
        dates=dates[dates<self.today]
        
        streak = 0
        
        for i in range(1, len(dates)):
            if dates.iloc[i-1] - dates.iloc[i] == timedelta(days=1):
                streak += 1
            else:
                break
        
        return streak

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
            habit_tracker.streak_date = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'streak_date']
            habit_tracker.setting_default = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'tracking_type']
            return redirect(url_for('tracker_redirect')) #trying this instead of the redirect for simple  
        else:
            error = "Login failed. Try again. Or sign-up for an account"
   
    return render_template('login.html', error=error)


@app.route('/register', methods=["GET", "POST"])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        tracking_type = request.form['tracking_type']

        # Check if passwords match
        if password != confirm_password:
            error = "Passwords do not match."
        else:
            # Load the logins.csv file
            df = pd.read_csv("logins.csv")

            # Check if username already exists
            if username in df['username'].values:
                error = "Username already exists. Please choose a different username."
            else:                
                # Append the new user to the DataFrame
                new_user = pd.DataFrame({
                    'username': [username],
                    'password': [password],
                    'tracking_type': [tracking_type],
                    'streak': [0],
                    'streak_date': ['']
                })
                df = pd.concat([df, new_user], ignore_index=True)
                
                # Save the updated DataFrame to logins.csv
                df.to_csv("logins.csv", index=False)

                # Create a daily_data.csv file for the user
                user_daily_file = f"{username}_daily_data.csv"
                if tracking_type=='default':
                    daily_data_df = pd.DataFrame(columns=['Date','Water','Exercise','Exercise2','Outside','Diet','Read','Picture','completed','streak_number'])  
                else:
                    daily_data_df = pd.DataFrame(columns=['Date','Water','Exercise','Exercise2','Outside','Diet','Read','Picture','completed','streak_number'])  #add rest of column to the extended tracking
                daily_data_df.to_csv(user_daily_file, index=False)

                return redirect(url_for('login'))

    return render_template('register.html', error=error)


#redirect page to deterime which checklist page will be displayed
@app.route('/tracker_redirect')
def tracker_redirect():
    if  habit_tracker.setting_default == 'default':
            return redirect(url_for('tracker_Default'))
    else:
        return redirect(url_for('tracker_Extended')) 


#updating checklist page for default layout, data pulled in from user for that date
@app.route('/tracker_Default', methods=['GET', 'POST'])
def tracker_Default():
    # Get today's entry if it exists
    today_entry = habit_tracker.daily_data[habit_tracker.daily_data['Date'] == habit_tracker.today]
    
    if request.method == 'POST':
        # Handle form submission
        water_intake = 'water_intake' in request.form  
        exercise_completed = 'exercise_completed' in request.form
        exercise_completed2 = 'exercise_completed2' in request.form
        exercise_outside = 'exercise_outside' in request.form
        diet_followed = 'diet_followed' in request.form
        read_pages = 'read_pages' in request.form
        picture_taken = 'picture_taken' in request.form
        
        # Update the habits in the CSV
        habit_tracker.track_habits(water_intake, exercise_completed, exercise_completed2, exercise_outside, diet_followed, read_pages, picture_taken)
        return redirect(url_for('tracker_redirect'))
    
    # If today's entry exists, extract its values to pre-populate the form
    if not today_entry.empty:
        today_entry_data = today_entry.iloc[0]  # Get the first (and only) row as a dict-like object
        return render_template('tracker_default.html', daily_data=today_entry_data.to_dict(), streak=habit_tracker.streak)

    
    # If no entry for today, render with empty/default form
    return render_template('tracker_default.html', daily_data={}, streak=habit_tracker.streak)


if __name__ == '__main__':
    app.run(debug=True)

