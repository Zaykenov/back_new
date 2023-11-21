import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify

CREATE_CUSTOMER_TABLE = (
    """CREATE TABLE IF NOT EXISTS CUSTOMER (
        user_id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        given_name VARCHAR(50) NOT NULL,
        surname VARCHAR(50) NOT NULL,
        city VARCHAR(50),
        phone_number VARCHAR(15),
        profile_description TEXT,
        password VARCHAR(255) NOT NULL
    )"""
)



CREATE_CAREGIVER_TABLE = (
    """CREATE TABLE IF NOT EXISTS CAREGIVER (
        caregiver_user_id SERIAL PRIMARY KEY,
        photo BYTEA,
        gender VARCHAR(10),
        caregiving_type VARCHAR(50) NOT NULL,
        hourly_rate DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (caregiver_user_id) REFERENCES CUSTOMER(user_id) ON DELETE CASCADE
    )"""
)

CREATE_MEMBER_TABLE = (
    """CREATE TABLE IF NOT EXISTS MEMBER (
        member_user_id SERIAL PRIMARY KEY,
        house_rules TEXT,
        FOREIGN KEY (member_user_id) REFERENCES CUSTOMER(user_id) ON DELETE CASCADE
    )"""
)

CREATE_ADDRESS_TABLE = (
    """CREATE TABLE IF NOT EXISTS ADDRESS (
        member_user_id SERIAL PRIMARY KEY,
        house_number VARCHAR(10) NOT NULL,
        street VARCHAR(100) NOT NULL,
        town VARCHAR(50) NOT NULL,
        FOREIGN KEY (member_user_id) REFERENCES MEMBER(member_user_id)
    )"""
)

CREATE_JOB_TABLE = (
    """CREATE TABLE IF NOT EXISTS JOB (
        job_id SERIAL PRIMARY KEY,
        member_user_id INT,
        required_caregiving_type VARCHAR(50) NOT NULL,
        other_requirements TEXT,
        date_posted DATE NOT NULL DEFAULT CURRENT_DATE,
        FOREIGN KEY (member_user_id) REFERENCES MEMBER(member_user_id)
    )"""
)

CREATE_JOB_APPLICATION_TABLE = (
    """CREATE TABLE IF NOT EXISTS JOB_APPLICATION (
        caregiver_user_id INT,
        job_id INT,
        date_applied DATE NOT NULL DEFAULT CURRENT_DATE,
        PRIMARY KEY (caregiver_user_id, job_id),
        FOREIGN KEY (caregiver_user_id) REFERENCES CAREGIVER(caregiver_user_id),
        FOREIGN KEY (job_id) REFERENCES JOB(job_id)
    )"""
)

CREATE_APPOINTMENT_TABLE = (
    """CREATE TABLE IF NOT EXISTS APPOINTMENT (
        appointment_id SERIAL PRIMARY KEY,
        caregiver_user_id INT,
        member_user_id INT,
        appointment_date DATE NOT NULL,
        appointment_time TIME NOT NULL,
        work_hours INT NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'Pending',
        FOREIGN KEY (caregiver_user_id) REFERENCES CAREGIVER(caregiver_user_id),
        FOREIGN KEY (member_user_id) REFERENCES MEMBER(member_user_id)
    )"""
)

INSERT_CUSTOMER = (
    """INSERT INTO CUSTOMER (
        email, given_name, surname, city, phone_number, profile_description, password
    ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING user_id"""
)

INSERT_CAREGIVER = (
    """INSERT INTO CAREGIVER (
        photo, gender, caregiving_type, hourly_rate
    ) VALUES (%s, %s, %s, %s) RETURNING caregiver_user_id"""
)

INSERT_MEMBER = (
    """INSERT INTO MEMBER (
        house_rules
    ) VALUES (%s) RETURNING member_user_id"""
)

INSERT_ADDRESS = (
    """INSERT INTO ADDRESS (
        member_user_id, house_number, street, town
    ) VALUES (%s, %s, %s, %s) RETURNING address_id"""
)

INSERT_JOB = (
    """INSERT INTO JOB (
        member_user_id, required_caregiving_type, other_requirements
    ) VALUES (%s, %s, %s) RETURNING job_id"""
)

INSERT_JOB_APPLICATION = (
    """INSERT INTO JOB_APPLICATION (
        caregiver_user_id, job_id
    ) VALUES (%s, %s) RETURNING application_id"""
)

INSERT_APPOINTMENT = (
    """INSERT INTO APPOINTMENT (
        caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status
    ) VALUES (%s, %s, %s, %s, %s, %s) RETURNING appointment_id"""
)

UPDATE_CUSTOMER = (
    """UPDATE CUSTOMER 
       SET email = %s, given_name = %s, surname = %s, city = %s, 
           phone_number = %s, profile_description = %s, password = %s 
       WHERE user_id = %s"""
)

DELETE_CUSTOMER = """DELETE FROM CUSTOMER WHERE user_id = %s"""

SELECT_CUSTOMER = """SELECT * FROM CUSTOMER WHERE user_id = %s"""

load_dotenv()
app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.route("/")  # Define the root route
def home():
    return "Welcome to the Customer API!"

@app.post("/api/customer")
def create_customer(): 
    data = request.get_json()
    email = data.get("email")
    given_name = data.get("given_name")
    surname = data.get("surname")
    city = data.get("city")
    phone_number = data.get("phone_number")
    profile_description = data.get("profile_description")
    password = data.get("password")

    with connection: 
        with connection.cursor() as cursor: 
            cursor.execute(CREATE_CUSTOMER_TABLE)
            cursor.execute(INSERT_CUSTOMER, (
                email, given_name, surname, city, phone_number, profile_description, password
            ))
            user_id = cursor.fetchone()[0]

    return {"id": user_id, "message": f"Customer {given_name} created."}, 201

@app.get("/api/customer/<int:user_id>")
def get_customer(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_CUSTOMER, (user_id,))
            customer = cursor.fetchone()
    if customer:
        return jsonify({"customer": customer}), 200
    else:
        return jsonify({"message": "Customer not found"}), 404

@app.put("/api/customer/<int:user_id>")
def update_customer(user_id):
    data = request.get_json()
    email = data.get("email")
    given_name = data.get("given_name")
    surname = data.get("surname")
    city = data.get("city")
    phone_number = data.get("phone_number")
    profile_description = data.get("profile_description")
    password = data.get("password")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_CUSTOMER, (
                email, given_name, surname, city, phone_number, profile_description, password, user_id
            ))

    return jsonify({"message": f"Customer {user_id} updated"}), 200

@app.delete("/api/customer/<int:user_id>")
def delete_customer(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_CUSTOMER, (user_id,))

    return jsonify({"message": f"Customer {user_id} deleted"}), 200

@app.post("/api/caregiver")
def create_caregiver():
    data = request.get_json()
    photo = data.get("photo")
    gender = data.get("gender")
    caregiving_type = data.get("caregiving_type")
    hourly_rate = data.get("hourly_rate")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_CAREGIVER_TABLE)
            cursor.execute(INSERT_CAREGIVER, (photo, gender, caregiving_type, hourly_rate))
            caregiver_user_id = cursor.fetchone()[0]

    return {"id": caregiver_user_id, "message": f"Caregiver created."}, 201

@app.post("/api/member")
def create_member():
    data = request.get_json()
    house_rules = data.get("house_rules")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_MEMBER_TABLE)
            cursor.execute(INSERT_MEMBER, (house_rules,))
            member_user_id = cursor.fetchone()[0]

    return {"id": member_user_id, "message": f"Member created."}, 201

@app.post("/api/address")
def create_address():
    data = request.get_json()
    member_user_id = data.get("member_user_id")
    house_number = data.get("house_number")
    street = data.get("street")
    town = data.get("town")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ADDRESS_TABLE)
            cursor.execute(INSERT_ADDRESS, (member_user_id, house_number, street, town))
            address_id = cursor.fetchone()[0]

    return {"id": address_id, "message": f"Address created."}, 201

@app.post("/api/job")
def create_job():
    data = request.get_json()
    member_user_id = data.get("member_user_id")
    required_caregiving_type = data.get("required_caregiving_type")
    other_requirements = data.get("other_requirements")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_JOB_TABLE)
            cursor.execute(INSERT_JOB, (member_user_id, required_caregiving_type, other_requirements))
            job_id = cursor.fetchone()[0]

    return {"id": job_id, "message": f"Job created."}, 201


if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True)



