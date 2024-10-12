import os
import pandas as pd
import flask
from flask import Flask, render_template, request, redirect, url_for
from datetime import date

app = Flask(__name__)

class HabitTracker:
    def __init__(self):
        self.login_data = pd.read_csv("logins.csv")
        self.daily_data = pd.read_csv("user_habits.csv")
        self.today = date.today()
        self.setting_default = True
    
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
                return redirect(url_for('tracker_redirect'))  
            else:
                error = "Login failed. Try again. Or sign-up for an account"
        return render_template('login.html', error=error)

    def checkLogin(self, username, password):
        return ((self.login_data['username'] == username) & (self.login_data['password'] == password)).any()

    @app.route('/tracker_redirect')
    def tracker_redirect(self):
        self.check_today_entry
        
        if habit_tracker.setting_default==True:
           return redirect( url_for ('tracker_d'))
        else:
            return render_template('tracker_e.html', daily_data=habit_tracker.daily_data)

    @app.route('/tracker_d', methods=['GET', 'POST'])
    def tracker_Default(self):
        if request.method == 'POST':
            water_intake = 'water_intake' in request.form  
            exercise_completed = 'exercise_completed' in request.form
            exercise_completed2 = 'exercise_completed2' in request.form
            exercise_outside = 'exercise_outside' in request.form
            diet_followed = 'diet_followed' in request.form
            read_pages = 'read_pages' in request.form
            picture_taken = 'picuture_taken' in request.form
            
            # Call the habit tracking function
            self.track_habits(water_intake, exercise_completed, exercise_completed2, exercise_outside, diet_followed, read_pages, picture_taken)
            return redirect(url_for('tracker_Default'))  
        return render_template('tracker_d.html', daily_data=habit_tracker.daily_data)
    
    
    
    

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

        habit_tracker.daily_data = pd.concat( habit_tracker.daily_data, pd.DataFrame([new_entry]), ignore_index=True)
        habit_tracker.daily_data.to_csv(habit_tracker.daily_data, index=False)
    
    def check_today_entry(self):
        today_entry = self.daily_data[self.daily_data['Date'] == self.today]
        if not today_entry.empty:
            print("Today's entry exists.")
            return today_entry.iloc[0]  # Return today's entry
        else:
            print("No entry for today.")
            return None  # Return None if no entry for today
        

habit_tracker = HabitTracker()

if __name__ == '__main__':
    app.run(debug=True)

    