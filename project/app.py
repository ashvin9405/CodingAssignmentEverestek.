import logging
import os
from datetime import datetime

from db_connection import db
from flask import Flask, request, jsonify
from flasgger import Swagger
from llm_model import get_name_origin
from models import User

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Flask App
app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://new_user:user_password@db/test_db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize Swagger
swagger = Swagger(app)

@app.route("/", methods=["GET"])
def homepage():
    """
    Basic health check route.
    ---
    responses:
      200:
        description: API is running successfully.
    """
    return jsonify({"message": "User APIs!"}), 200


@app.route("/users", methods=["POST"])
def add_user():
    """
    Add a new user.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
            - age
            - dob
            - university_grade
          properties:
            first_name:
              type: string
              example: John
            last_name:
              type: string
              example: Doe
            age:
              type: integer
              example: 25
            dob:
              type: string
              format: date
              example: "1998-05-20"
            university_grade:
              type: number
              example: 3.5
    responses:
      201:
        description: User added successfully
      400:
        description: Bad request (missing or invalid data)
      500:
        description: Internal server error
    """
    data = request.get_json()

    required_fields = ["first_name", "last_name", "age", "dob", "university_grade"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        dob = datetime.strptime(data["dob"], "%Y-%m-%d").date()
        if data["age"] <= 0:
            return jsonify({"error": "Age must be a positive number"}), 400
        if not (0 <= data["university_grade"] <= 4):
            return jsonify({"error": "University grade must be between 0 and 4"}), 400

        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            dob=dob,
            university_grade=data["university_grade"]
        )

        db.session.add(user)
        db.session.commit()
        logging.info("New user added: %s %s %s", user.first_name, user.last_name, user.id)

        return jsonify({"message": "User added successfully", "user_id": user.id}), 201

    except ValueError as ve:
        logging.error("Date format error: %s", str(ve))
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        logging.error("Error adding user: %s", str(e))
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Retrieve a user by ID with name origin from LLM.
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        type: integer
        example: 1
    responses:
      200:
        description: Successfully retrieved user data.
      404:
        description: User not found.
      500:
        description: Internal server error.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        name_origin = get_name_origin(user.first_name)

        logging.info("Fetched user details for ID: %s", user_id)

        return jsonify({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age,
            "dob": user.dob.strftime("%Y-%m-%d"),
            "university_grade": user.university_grade,
            "name_origin": name_origin
        }), 200

    except Exception as e:
        logging.error("Error fetching user details: %s", str(e))
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
