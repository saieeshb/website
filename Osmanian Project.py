# OSMECON Event Check System
# Shows students which events they signed up for
from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(script_dir, 'events.xlsx')

print(f"Looking for Excel file at: {excel_path}")
print(f"File exists: {os.path.exists(excel_path)}")

# Load the events data
df = pd.read_excel(excel_path)
print(f"Loaded {len(df)} student records")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    uid = request.form['student_id'].strip()
    
    # Find the student's events
    student_data = df[df['uid'] == uid]
    
    if not student_data.empty:
        # Get student info
        student_name = student_data.iloc[0]['name']
        
        # Get the events with locations (filter out empty values)
        events = []
        
        event1 = student_data.iloc[0]['event_catogorery']
        location1 = student_data.iloc[0]['event_location']
        if pd.notna(event1) and event1 != "":
            events.append({'name': event1, 'location': location1})
        
        event2 = student_data.iloc[0]['event_catogery1']
        location2 = student_data.iloc[0]['event_location1']
        if pd.notna(event2) and event2 != "":
            events.append({'name': event2, 'location': location2})
        
        if events:
            # Redirect to results page
            return render_template('results.html', 
                                uid=uid, 
                                student_name=student_name,
                                events=events)
        else:
            message = "No events registered for this UID"
            return render_template('index.html', message=message, error=True)
    else:
        message = "UID not found. Please check your UID and try again."
        return render_template('index.html', message=message, error=True)

if __name__ == '__main__':
    app.run(debug=True)