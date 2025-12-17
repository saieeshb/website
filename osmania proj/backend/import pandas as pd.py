import pandas as pd

# Create sample data for student events
uids = []
names = []
event_categories = []
event_locations = []
event_categories1 = []
event_locations1 = []

# Sample events with their locations
events_with_locations = [
    ("Workshop on Clinical Skills", "Room 101, Medical Block"),
    ("Medical Ethics Seminar", "Auditorium A"),
    ("Anatomy Lab Session", "Anatomy Lab, 2nd Floor"),
    ("Cardiology Conference", "Conference Hall B"),
    ("Surgery Demonstration", "Operating Theater 1"),
    ("Pharmacology Quiz", "Room 205, Academic Block"),
    ("Pathology Workshop", "Pathology Lab"),
    ("Radiology Training", "Radiology Department")
]

# Sample student names
first_names = ["Rahul", "Priya", "Arjun", "Sneha", "Rohan", "Ananya", "Karthik", "Divya", "Aditya", "Meera"]
last_names = ["Sharma", "Patel", "Kumar", "Reddy", "Singh", "Iyer", "Rao", "Mehta", "Gupta", "Nair"]

# Generate 50 sample student records
for i in range(1, 51):
    uids.append(f"OSMEC-{10000 + i}")
    # Generate random name
    names.append(f"{first_names[i % len(first_names)]} {last_names[i % len(last_names)]}")
    
    # Assign first event
    event_data = events_with_locations[i % len(events_with_locations)]
    event_categories.append(event_data[0])
    event_locations.append(event_data[1])
    
    # Some students have a second event, some don't
    if i % 3 == 0:
        event_data2 = events_with_locations[(i + 2) % len(events_with_locations)]
        event_categories1.append(event_data2[0])
        event_locations1.append(event_data2[1])
    else:
        event_categories1.append("")
        event_locations1.append("")

# Create DataFrame
data = {
    'uid': uids,
    'name': names,
    'event_catogorery': event_categories,
    'event_location': event_locations,
    'event_catogery1': event_categories1,
    'event_location1': event_locations1
}

df = pd.DataFrame(data)

# Save to Excel file
df.to_excel('events.xlsx', index=False, engine='openpyxl')

print("✅ events.xlsx created successfully!")
print(f"📊 Total students: {len(df)}")
print(f"📋 Columns: uid, name, event_catogorery, event_location, event_catogery1, event_location1")
print("\nFirst 10 entries:")
print(df.head(10))
print("\nFile saved as: events.xlsx")
print("👉 Move this file to your backend folder!")