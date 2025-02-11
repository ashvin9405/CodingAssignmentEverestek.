
import json
from app import db, app
from models import User  # Import User model
from datetime import datetime

def reset_database():
    """Drops all tables, recreates them, and inserts multiple users from a JSON file."""
    with app.app_context():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Recreate tables

        try:
            # Load user data from JSON file
            with open("users.json", "r",encoding="utf-8") as file:
                users_data = json.load(file)

            # Convert JSON data into User objects
            users_to_insert = [
                User(
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    age=user["age"],
                    dob=datetime.strptime(user["dob"], "%Y-%m-%d").date(),  # Convert DOB to date object
                    university_grade=user["university_grade"]
                )
                for user in users_data
            ]

            # Bulk insert all users at once
            db.session.bulk_save_objects(users_to_insert)
            db.session.commit()

            print(f"Inserted {len(users_to_insert)} users successfully!")

        except Exception as e:
            db.session.rollback()
            print(f"Error inserting users: {str(e)}")

if __name__ == "__main__":
    reset_database()