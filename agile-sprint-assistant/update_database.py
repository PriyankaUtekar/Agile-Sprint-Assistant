"""
Update database with new models for retrospectives
"""

import os

# Delete old database
db_path = 'database/agile_assistant.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Deleted old database")

# Initialize new database with updated models
from database.models import init_database
init_database()

# Generate sample data
print("\n🎨 Generating sample data...")
os.system('python sample_data/generate_sample_data.py')

print("\n✅ Database updated with retrospective models!")