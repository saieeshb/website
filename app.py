# OSMECON Event Check System
# Shows students which events they signed up for
from flask import Flask, request, render_template, send_from_directory, send_file
import pandas as pd
import os
import re

# =========================
# FLASK CONFIGURATION - FIXED
# =========================

# Get absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))  # backend/ folder
frontend_dir = os.path.join(script_dir, '..', 'frontend')
static_dir = os.path.join(frontend_dir, 'static')

print(f"Backend directory: {script_dir}")
print(f"Frontend directory: {frontend_dir}")
print(f"Static directory: {static_dir}")
print(f"Frontend exists: {os.path.exists(frontend_dir)}")
print(f"Static exists: {os.path.exists(static_dir)}")

# List files in frontend directory
print("\nFiles in frontend directory:")
for file in os.listdir(frontend_dir):
    print(f"  {file}")

app = Flask(__name__)

excel_path = os.path.join(script_dir, 'event123.xlsx')
print(f"\nLooking for Excel file at: {excel_path}")
print(f"Excel file exists: {os.path.exists(excel_path)}")

# =========================
# FIXED ROUTES FOR HTML PAGES
# =========================

@app.route('/')
def index():
    print(f"[ROUTE] / -> Rendering index.html from {frontend_dir}")
    return render_template('index.html')

@app.route('/schedule')
def schedule():
    print(f"[ROUTE] /schedule -> Rendering schedule.html from {frontend_dir}")
    return render_template('schedule.html')

@app.route('/results')
def results():
    print(f"[ROUTE] /results -> Rendering results.html from {frontend_dir}")
    return render_template('results.html')

# =========================
# STATIC FILE ROUTES FOR PDF (KEEP EXISTING)
# =========================


@app.route('/event_schedule.pdf')
def serve_event_pdf():
    """Direct route for event schedule PDF"""
    # Try multiple possible locations
    possible_paths = [
        os.path.join(frontend_dir, 'event_schedule.pdf'),
        os.path.join(static_dir, 'event_schedule.pdf'),
        os.path.join(frontend_dir, 'events_schedule.pdf'),
        os.path.join(static_dir, 'events_schedule.pdf'),
    ]
    
    for pdf_path in possible_paths:
        if os.path.exists(pdf_path):
            print(f"\n[PDF Route] Found PDF at: {pdf_path}")
            return send_file(pdf_path, as_attachment=False)
    
    print(f"\n[PDF Route] PDF not found in any location")
    return "Event schedule PDF not found. Please check if the file exists.", 404

# =========================
# REST OF YOUR EXISTING CODE (UNCHANGED)
# =========================

# Load the student registration sheet
df = pd.read_excel(excel_path, sheet_name='Final')

# Normalize ID column
df['OSMEC-ID'] = df['OSMEC-ID'].astype(str).str.strip().str.upper()

print(f"\nLoaded {len(df)} student records from 'Final' sheet")
print(f"First 5 IDs: {df['OSMEC-ID'].head().tolist()}")

# Dictionary to store workshop, event, and subject details
WORKSHOP_DETAILS = {}
EVENT_DETAILS = {}
SUBJECT_DETAILS = {}

# =========================
# LOAD LOOKUP SHEETS
# =========================

# Load Workshop sheet
try:
    workshop_df = pd.read_excel(excel_path, sheet_name='Workshop')
    print(f"\n'Workshop' sheet columns: {list(workshop_df.columns)}")

    w_code_col = None
    w_name_col = None
    w_location_col = None

    for col in workshop_df.columns:
        col_upper = str(col).strip().upper()
        if 'ID' in col_upper or 'CODE' in col_upper:
            w_code_col = col
        elif 'WORKSHOP' in col_upper or 'NAME' in col_upper:
            w_name_col = col
        elif 'LOCATION' in col_upper or 'VENUE' in col_upper:
            w_location_col = col

    if w_code_col and w_name_col and w_location_col:
        for _, row in workshop_df.iterrows():
            code = str(row[w_code_col]).strip()
            name = str(row[w_name_col]).strip()
            location = str(row[w_location_col]).strip()

            if code and code.lower() != 'nan':
                WORKSHOP_DETAILS[code] = {
                    'name': name,
                    'location': location
                }
        print(f"Loaded {len(WORKSHOP_DETAILS)} workshops")

except Exception as e:
    print(f"Warning: Could not load Workshop sheet: {e}")

# Load Events sheet - WITH DEBUGGING
try:
    events_df = pd.read_excel(excel_path, sheet_name='Events')
    print(f"\n'Events' sheet columns: {list(events_df.columns)}")
    
    # DEBUG: Show first few rows
    print("\nFirst 5 rows of Events sheet:")
    print(events_df.head())
    print()

    e_code_col = None
    e_name_col = None
    e_location_col = None

    for col in events_df.columns:
        col_upper = str(col).strip().upper()
        if 'ID' in col_upper or 'CODE' in col_upper:
            e_code_col = col
            print(f"  Using '{col}' as event code column")
        elif 'EVENT' in col_upper or 'NAME' in col_upper:
            e_name_col = col
            print(f"  Using '{col}' as event name column")
        elif 'LOCATION' in col_upper or 'VENUE' in col_upper:
            e_location_col = col
            print(f"  Using '{col}' as event location column")

    if e_code_col and e_name_col and e_location_col:
        for _, row in events_df.iterrows():
            event_id = str(row[e_code_col]).strip()
            event_name = str(row[e_name_col]).strip()
            location = str(row[e_location_col]).strip()

            if event_id and event_id.lower() != 'nan':
                EVENT_DETAILS[event_id] = {
                    'name': event_name,
                    'location': location
                }
                print(f"  Loaded event: '{event_id}' -> '{event_name}' at '{location}'")
        print(f"\nLoaded {len(EVENT_DETAILS)} events")

except Exception as e:
    print(f"Warning: Could not load Events sheet: {e}")

# Load Subjects sheet - CORRECTED BASED ON YOUR DATA
try:
    subjects_df = pd.read_excel(excel_path, sheet_name='Subjects')
    print(f"\n'Subjects' sheet columns: {list(subjects_df.columns)}")

    s_code_col = 'SubjectID'  # This contains S001, S002, etc.
    s_name_col = 'SUBJECT_NAME'  # This contains OPTHALMOLOGY, etc.
    s_location_col = 'LOCATION'  # This contains location
    
    print(f"Using columns for Subjects:")
    print(f"  Code column (SubjectID): {s_code_col}")
    print(f"  Name column (SUBJECT_NAME): {s_name_col}")
    print(f"  Location column (LOCATION): {s_location_col}")

    if s_code_col in subjects_df.columns and s_name_col in subjects_df.columns:
        for _, row in subjects_df.iterrows():
            subject_id = str(row[s_code_col]).strip()
            subject_name = str(row[s_name_col]).strip()
            location = str(row[s_location_col]).strip() if s_location_col in subjects_df.columns else "Location TBA"

            if subject_id and subject_id.lower() != 'nan':
                SUBJECT_DETAILS[subject_id] = {
                    'name': subject_name,
                    'location': location
                }
        print(f"\nLoaded {len(SUBJECT_DETAILS)} subjects")
        
        # DEBUG: Print some sample subject mappings
        print("\nSample subject mappings (first 10):")
        for i, (code, details) in enumerate(list(SUBJECT_DETAILS.items())[:10]):
            print(f"  '{code}' -> '{details['name']}' at '{details['location']}'")
        
    else:
        print("Warning: Required columns not found in Subjects sheet")
        print(f"Available columns: {list(subjects_df.columns)}")

except Exception as e:
    print(f"Warning: Could not load Subjects sheet: {e}")

# =========================
# COLUMN DETECTION
# =========================
all_columns = df.columns.tolist()

# Detect event columns (DAY_X_EVENT_Y pattern)
event_columns = []
subject_columns = []

for col in all_columns:
    col_str = str(col)
    col_upper = col_str.upper()
    
    # Check for event columns - look for DAY_X_EVENT_Y pattern
    if re.match(r'DAY_\d+_EVENT_\d+$', col_upper):
        event_columns.append(col)
    # Check for subject columns - look for DAY_X_EVENT_Y_SUBJECT_Z pattern
    elif re.match(r'DAY_\d+_EVENT_\d+_SUBJECT_\d+$', col_upper):
        subject_columns.append(col)

print(f"\nDetected {len(event_columns)} event columns")
print(f"Event columns: {event_columns}")

print(f"\nDetected {len(subject_columns)} subject columns")
print(f"Subject columns: {subject_columns}")

# =========================
# HELPER FUNCTIONS
# =========================
def normalize_column_name(col_name):
    """Convert column name to consistent uppercase format"""
    col_str = str(col_name).upper()
    # Remove any extra spaces and ensure consistent underscores
    col_str = col_str.strip().replace(' ', '_')
    return col_str

def parse_day_from_column(col_name):
    """Extract day number from column name like DAY_1_EVENT_1"""
    col_norm = normalize_column_name(col_name)
    match = re.match(r'DAY_(\d+)', col_norm)
    return int(match.group(1)) if match else 0

def parse_event_from_column(col_name):
    """Extract event number from column name like DAY_1_EVENT_1"""
    col_norm = normalize_column_name(col_name)
    match = re.match(r'DAY_\d+_EVENT_(\d+)', col_norm)
    return int(match.group(1)) if match else 0

def get_event_prefix(col_name):
    """Get normalized event prefix from column name"""
    col_norm = normalize_column_name(col_name)
    
    # For event columns (DAY_X_EVENT_Y)
    if re.match(r'DAY_\d+_EVENT_\d+$', col_norm):
        # Extract DAY_X_EVENT_Y pattern
        match = re.match(r'(DAY_\d+_EVENT_\d+)', col_norm)
        if match:
            return match.group(1)
    
    # For subject columns (DAY_X_EVENT_Y_SUBJECT_Z)
    match = re.match(r'(DAY_\d+_EVENT_\d+)_SUBJECT_\d+', col_norm)
    if match:
        return match.group(1)
    
    return None

def get_workshop_details(workshop_code):
    if workshop_code in WORKSHOP_DETAILS:
        return WORKSHOP_DETAILS[workshop_code]
    return {'name': workshop_code, 'location': 'Location TBA'}

def get_event_details(event_code):
    """Get event details with better debugging"""
    event_code_clean = str(event_code).strip()
    event_code_upper = event_code_clean.upper()
    
    print(f"    Looking up event: '{event_code_clean}'")
    
    # Try exact match first
    if event_code_clean in EVENT_DETAILS:
        details = EVENT_DETAILS[event_code_clean]
        print(f"    Found exact match: '{details['name']}' at '{details['location']}'")
        return details
    
    # Try uppercase version
    elif event_code_upper in EVENT_DETAILS:
        details = EVENT_DETAILS[event_code_upper]
        print(f"    Found uppercase match: '{details['name']}' at '{details['location']}'")
        return details
    
    # Check if it's a partial match
    for key, details in EVENT_DETAILS.items():
        if event_code_clean in key or key in event_code_clean:
            print(f"    Found partial match: {key} -> '{details['name']}' at '{details['location']}'")
            return details
    
    print(f"    WARNING: Event code '{event_code_clean}' not found, using default")
    return {'name': event_code_clean, 'location': 'Location TBA'}

def get_subject_details(subject_code):
    """Get subject details, with debugging"""
    # Clean up the subject code
    subject_code_clean = str(subject_code).strip()
    
    if subject_code_clean in SUBJECT_DETAILS:
        details = SUBJECT_DETAILS[subject_code_clean]
        return details
    else:
        # Try uppercase version
        subject_code_upper = subject_code_clean.upper()
        if subject_code_upper in SUBJECT_DETAILS:
            details = SUBJECT_DETAILS[subject_code_upper]
            return details
        else:
            print(f"    WARNING: Subject code '{subject_code_clean}' not found in SUBJECT_DETAILS")
            return {'name': f"Subject {subject_code_clean}", 'location': 'Location TBA'}

# =========================
# CHECK ROUTE (FIXED)
# =========================

@app.route('/check', methods=['POST'])
def check():
    student_id = request.form['student_id'].strip().upper()
    print(f"\n{'='*60}")
    print(f"Looking for ID: {student_id}")
    print(f"{'='*60}")

    student_data = df[df['OSMEC-ID'] == student_id]

    if student_data.empty:
        message = f"ID not found: {student_id}. Please check your ID and try again. ID should be 4 digits."
        print(message)
        return render_template('index.html', message=message, error=True)

    student_name = student_data.iloc[0]['FULL NAME']
    print(f"Found student: {student_name}")

    # Get workshop (from WORKSHOP column - Day 1)
    workshop = None
    workshop_code = student_data.iloc[0]['WORKSHOP']
    if pd.notna(workshop_code) and str(workshop_code).strip() != "" and str(workshop_code).strip().lower() != "nan":
        workshop_code_str = str(workshop_code).strip()
        workshop_details = get_workshop_details(workshop_code_str)
        workshop = {
            'name': workshop_details['name'],
            'location': workshop_details['location']
        }
        print(f"Workshop: {workshop_code_str} -> '{workshop['name']}' at '{workshop['location']}'")

    # Organize events by day
    events_by_day = {}

    for col in sorted(event_columns):
        event_code = student_data.iloc[0][col]

        if pd.notna(event_code) and str(event_code).strip() != "" and str(event_code).strip().lower() != "nan":
            event_code_str = str(event_code).strip()
            event_details = get_event_details(event_code_str)

            day = parse_day_from_column(col)
            event_prefix = get_event_prefix(col)
            
            print(f"\n{'='*40}")
            print(f"Processing event column: {col}")
            print(f"  Day: {day}")
            print(f"  Event code: '{event_code_str}'")
            print(f"  Event name: '{event_details['name']}'")
            print(f"  Event location from lookup: '{event_details['location']}'")

            # Find subjects for this event
            subjects = []
            
            if subject_columns:
                print(f"\n  Looking for subjects...")
                
                for sub_col in subject_columns:
                    sub_prefix = get_event_prefix(sub_col)
                    
                    # Check if this subject column belongs to the current event
                    if sub_prefix and sub_prefix == event_prefix:
                        subject_code_raw = student_data.iloc[0][sub_col]
                        
                        if pd.notna(subject_code_raw) and str(subject_code_raw).strip() != "" and str(subject_code_raw).strip().lower() != "nan":
                            subject_code_str = str(subject_code_raw).strip()
                            print(f"  Found in {sub_col}: subject code = '{subject_code_str}'")
                            
                            subject_details = get_subject_details(subject_code_str)
                            subjects.append({
                                'name': subject_details['name'],
                                'location': subject_details['location']
                            })
                            print(f"    Subject name: '{subject_details['name']}'")
                            print(f"    Subject location: '{subject_details['location']}'")
                        else:
                            print(f"  {sub_col} has no data")
                else:
                    print(f"  No subject columns match this event prefix")

            if day not in events_by_day:
                events_by_day[day] = []

            # FIXED: Use event location directly, don't override with subject location
            event_location = event_details['location']
            print(f"  Final event location: '{event_location}'")

            events_by_day[day].append({
                'name': event_details['name'],
                'location': event_location,  # Always use the event's own location
                'subjects': subjects
            })

            print(f"\n  Result: Event '{event_details['name']}' at '{event_location}' with {len(subjects)} subjects")

    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Student: {student_name} ({student_id})")
    print(f"  Workshop: {'Yes' if workshop else 'No'}")
    
    total_events = sum(len(v) for v in events_by_day.values())
    print(f"  Events: {total_events} across {len(events_by_day)} days")
    
    # Print detailed event and subject count
    total_subjects = 0
    for day in sorted(events_by_day.keys()):
        events = events_by_day[day]
        day_subjects = sum(len(event['subjects']) for event in events)
        total_subjects += day_subjects
        print(f"  Day {day}: {len(events)} events, {day_subjects} subjects")
    
    print(f"  Total subjects: {total_subjects}")
    print(f"{'='*60}")

    # DEBUG: Show final data structure
    print("\nFINAL DATA STRUCTURE:")
    for day, events in sorted(events_by_day.items()):
        print(f"\nDay {day}:")
        for i, event in enumerate(events, 1):
            print(f"  Event {i}: '{event['name']}' at '{event['location']}'")
            for j, subject in enumerate(event['subjects'], 1):
                print(f"    Subject {j}: '{subject['name']}' at '{subject['location']}'")

    if not workshop and total_events == 0:
        message = "No workshops or events registered for this ID"
        return render_template('index.html', message=message, error=True)

    return render_template(
        'results.html',
        uid=student_id,
        student_name=student_name,
        workshop=workshop,
        events_by_day=sorted(events_by_day.items())
    )

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print("FLASK SERVER STARTING")
    print("Available routes:")
    print("  http://localhost:5000/           - Home page")
    print("  http://localhost:5000/schedule   - Schedule page")
    print("  http://localhost:5000/results    - Results page (redirect)")
    print("  http://localhost:5000/check      - Check student (POST)")
    print(f"{'='*60}\n")
    app.run(debug=True, port=5000)