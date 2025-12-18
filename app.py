# OSMECON Event Check System
# Shows students which events they signed up for
from flask import Flask, request, render_template
import pandas as pd
import os

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')

script_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(script_dir, 'events.xlsx')
locations_path = os.path.join(script_dir, 'event_locations.xlsx')

print(f"Looking for Excel file at: {excel_path}")
print(f"File exists: {os.path.exists(excel_path)}")


df = pd.read_excel(excel_path)

# Normalize UID column
df['uid'] = df['uid'].astype(str).str.strip().str.upper()

print(f"Loaded {len(df)} student records")
print(f"First 5 UIDs: {df['uid'].head().tolist()}")


EVENT_COLUMNS = sorted(
    [col for col in df.columns if col.startswith('event_category-')]
)

print(f"Detected {len(EVENT_COLUMNS)} event columns:")
print(EVENT_COLUMNS)


EVENT_LOCATIONS = {}

if os.path.exists(locations_path):
    locations_df = pd.read_excel(locations_path)

    for _, row in locations_df.iterrows():
        event_name = str(row['event_name']).strip()
        location = str(row['location']).strip()

        EVENT_LOCATIONS[event_name.lower()] = {
            'display_name': event_name,
            'location': location
        }

    print(f"Loaded {len(EVENT_LOCATIONS)} event locations from file")

else:
    print("event_locations.xlsx not found. Auto-generating from events.xlsx...")

    unique_events_dict = {}  # lowercase -> original name

    for col in EVENT_COLUMNS:
        events = df[col].dropna()
        events = events[events.astype(str).str.strip() != '']
        events = events[events.astype(str).str.lower() != 'nan']

        for event in events:
            event_name = str(event).strip()
            event_lower = event_name.lower()

            if event_lower not in unique_events_dict:
                unique_events_dict[event_lower] = event_name

    unique_events = sorted(unique_events_dict.values())

    locations_df = pd.DataFrame({
        'event_name': unique_events,
        'location': ['Location TBA - Please check notice board'] * len(unique_events)
    })

    locations_df.to_excel(locations_path, index=False, engine='openpyxl')

    for event_name in unique_events:
        EVENT_LOCATIONS[event_name.lower()] = {
            'display_name': event_name,
            'location': 'Location TBA - Please check notice board'
        }

# =========================
# HELPER FUNCTION
# =========================
def get_event_location(event_name):
    event_lower = event_name.lower()
    if event_lower in EVENT_LOCATIONS:
        return EVENT_LOCATIONS[event_lower]['location']
    return "Location TBA - Please check notice board"

# =========================
# ROUTES
# =========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    uid = request.form['student_id'].strip().upper()
    print(f"Looking for UID: {uid}")

    student_data = df[df['uid'] == uid]

    if student_data.empty:
        message = f"ID not found: {uid}. Please check your ID and try again."
        print(message)
        return render_template('index.html', message=message, error=True)

    student_name = student_data.iloc[0]['fullname']
    print(f"Found student: {student_name}")

    events = []

    for col in EVENT_COLUMNS:
        event_value = student_data.iloc[0][col]

        if (
            pd.notna(event_value)
            and str(event_value).strip() != ""
            and str(event_value).strip().lower() != "nan"
        ):
            event_name = str(event_value).strip()
            events.append({
                'name': event_name,
                'location': get_event_location(event_name)
            })

    print(f"Total events found: {len(events)}")

    if not events:
        message = "No events registered for this ID"
        return render_template('index.html', message=message, error=True)

    return render_template(
        'results.html',
        uid=uid,
        student_name=student_name,
        events=events
    )

if __name__ == '__main__':
    app.run(debug=True)
