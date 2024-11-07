import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta

app = Flask(__name__)

class HabitTracker:
    def __init__(self):
        self.login_data = pd.read_csv("logins.csv")
        self.daily_data = pd.read_csv("user_habits.csv")
        self.today = date.today().strftime('%Y-%m-%d')
        self.setting_default = True
        self.username = ""
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
                'Done': False  
            }
            self.daily_data = pd.concat([self.daily_data, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            # Update the existing entry
            idx = self.daily_data[self.daily_data['Date'] == self.today].index[0]
            self.daily_data.at[idx, 'Water'] = water_intake
            self.daily_data.at[idx, 'Exercise'] = exercise_completed
            self.daily_data.at[idx, 'Exercise2'] = exercise_completed2
            self.daily_data.at[idx, 'Outside'] = exercise_outside
            self.daily_data.at[idx, 'Diet'] = diet_followed
            self.daily_data.at[idx, 'Read'] = read_pages
            self.daily_data.at[idx, 'Picture'] = picture_taken
        
        # Check if all tasks are completed
        self.check_all_tasks_completed(self.today)
        self.update_streak()

        # Save updated data to CSV
        self.daily_data.to_csv(f"{self.username}_daily_data.csv", index=False)

    def check_all_tasks_completed(self, date_check):
        # Get today's entry
        check_entry = self.daily_data[self.daily_data['Date'] == date_check].iloc[0]
        
        # Check if all tasks are completed (assuming 'True' or 'completed' for each task)
        all_tasks = [
            check_entry['Water'],
            check_entry['Exercise'],
            check_entry['Exercise2'],
            check_entry['Outside'],
            check_entry['Diet'],
            check_entry['Read'],  
            check_entry['Picture']
        ]
        
        # If all are True, mark the day as completed
        if all(all_tasks):
            self.daily_data.loc[self.daily_data['Date'] == date_check, 'Done'] = True
        else:
            self.daily_data.loc[self.daily_data['Date'] == date_check, 'Done'] = False
        
        
    def check_streak(self):
        yesterday_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        if (yesterday_str == self.streak_date) and self.check_all_tasks_completed(yesterday_str):
            return True
        else:
            return False

    def update_streak(self):
        if int(self.streak) > 0:
            if self.check_streak() and self.check_all_tasks_completed(self.today):
                self.streak += 1
        elif self.check_all_tasks_completed(self.today):
            self.streak = 1
            
        idx = self.login_data[self.login_data['username'] == self.username].index[0]
        self.login_data.at[idx, 'streak'] = self.streak
        self.daily_data.at[idx, 'steak_date'] = self.today
        self.login_data.to_csv("logins.csv", index=False)

            
            
            
            
            
            
        
        
        

        

habit_tracker = HabitTracker()

@app.route('/')
def home():
    return render_template('login.html')

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
            habit_tracker.streak = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'streak'] 
            habit_tracker.streak_date = habit_tracker.login_data.loc[habit_tracker.login_data['username'] == habit_tracker.username, 'streak_date']
            return redirect(url_for('tracker_redirect'))  
        else:
            error = "Login failed. Try again. Or sign-up for an account"
    return render_template('login.html', error=error)

@app.route('/tracker_redirect')
def tracker_redirect():
    if  habit_tracker.check_today_entry()==None :
        if habit_tracker.setting_default:
            return redirect(url_for('tracker_Default'))
        else:
            streak = int(habit_tracker.streak.values[0])
            return render_template('tracker_e.html', daily_data=habit_tracker.daily_data, streak=streak)
    else:
        return redirect(url_for('tracker_Updating'))

@app.route('/tracker_Default', methods=['GET', 'POST'])
def tracker_Default():
    if request.method == 'POST':
        water_intake = 'water_intake' in request.form  
        exercise_completed = 'exercise_completed' in request.form
        exercise_completed2 = 'exercise_completed2' in request.form
        exercise_outside = 'exercise_outside' in request.form
        diet_followed = 'diet_followed' in request.form
        read_pages = 'read_pages' in request.form
        picture_taken = 'picture_taken' in request.form
        
        habit_tracker.track_habits(water_intake, exercise_completed, exercise_completed2, exercise_outside, diet_followed, read_pages, picture_taken)
        return redirect(url_for('tracker_redirect'))  
    return render_template('tracker_d.html', daily_data=habit_tracker.daily_data, streak=habit_tracker.streak)

@app.route('/tracker_Updating', methods=['GET', 'POST'])
def tracker_Updating():
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
        return render_template('tracker_updating.html', daily_data=today_entry_data)
    
    # If no entry for today, render with empty/default form
    return render_template('tracker_updating.html', daily_data={})


if __name__ == '__main__':
    app.run(debug=True)