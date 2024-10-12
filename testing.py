import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import date

app = Flask(__name__)

class HabitTracker:
    def __init__(self):
        self.login_data = pd.read_csv("logins.csv")
        self.daily_data = pd.read_csv("user_habits.csv")
        self.today = date.today()
        self.setting_default = True
        self.username=""
        self.streak=""
    
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
        new_entry = {
            'Date': pd.Timestamp.today(), 
            'Water': water_intake, 
            'Exercise': exercise_completed, 
            'Exercise2': exercise_completed2, 
            'Outside': exercise_outside, 
            'Diet': diet_followed, 
            'Read': read_pages,
            'Picture': picture_taken
        }

        # Check if there's already an entry for today
        today_str = pd.Timestamp.today().strftime('%Y-%m-%d')
        existing_entry_index = self.daily_data[self.daily_data['Date'].str.startswith(today_str)].index

        if not existing_entry_index.empty:
            # Update the existing entry
            self.daily_data.loc[existing_entry_index, list(new_entry.keys())[1:]] = list(new_entry.values())[1:]
        else:
            # Add a new entry
            self.daily_data = pd.concat([self.daily_data, pd.DataFrame([new_entry])], ignore_index=True)

        # Save the updated data to CSV
        self.daily_data.to_csv("user_habits.csv", index=False)

        

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
            return render_template('tracker_e.html', daily_data=habit_tracker.daily_data)
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
    return render_template('tracker_d.html', daily_data=habit_tracker.daily_data)

@app.route('/tracker_Updating', methods=['GET', 'POST'])
def tracker_Updating():
    
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
    return render_template('testing2.html', daily_data=habit_tracker.daily_data)

if __name__ == '__main__':
    app.run(debug=True)
