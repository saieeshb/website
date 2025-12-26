import pandas as pd

df = pd.read_excel('events1.xlsx', sheet_name='Workshop')
print("Workshop sheet columns:")
print(list(df.columns))
print("\nFirst few rows:")
print(df.head())
