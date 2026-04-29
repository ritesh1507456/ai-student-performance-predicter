
import os
import json
import sqlite3
import numpy as np
import joblib
import warnings
warnings.filterwarnings("ignore")
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"
DATABASE = "database.db"

try:
    model = joblib.load("model/model.pkl")
    scaler = joblib.load("model/scaler.pkl")
    print("✅ Model Loaded Successfully!")
except:
    print("❌ Model not found. Run train_model.py first.")
    model = None
    scaler = None

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE username=?", (username,))
        existing = cursor.fetchone()
        if existing:
            flash("Username already exists!")
            conn.close()
            return redirect("/student_register")
        cursor.execute(""" INSERT INTO students (name, email, username, password) VALUES (?, ?, ?, ?) """, (name, email, username, password))
        conn.commit()
        conn.close()
        flash("Registration Successful! Please login.")
        return redirect("/student_login")
    return render_template("student_register.html")

@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE username=?", (username,))
        student = cursor.fetchone()
        conn.close()
        if student and check_password_hash(student["password"], password):
            session["student_id"] = student["id"]
            session["student_name"] = student["name"]
            flash("Login Successful!")
            return redirect("/")
        flash("Invalid Username or Password")
    return render_template("student_login.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "student_id" not in session:
        flash("Please login first.")
        return redirect("/student_login")
    if not model or not scaler:
        return "Model not trained."
    try:
        study = float(request.form["study_hours"])
        attendance = float(request.form["attendance"])
        previous = float(request.form["previous_marks"])
        assignments = float(request.form["assignments"])
        sleep = float(request.form["sleep_hours"])
        input_data = np.array([[study, attendance, previous, assignments, sleep]])
        input_scaled = scaler.transform(input_data)
        prediction = float(model.predict(input_scaled)[0])
        if prediction >= 85:
            category = "Excellent"
            risk_level = "Low Risk"
        elif prediction >= 70:
            category = "Good"
            risk_level = "Low Risk"
        elif prediction >= 50:
            category = "Average"
            risk_level = "Medium Risk"
        else:
            category = "Needs Improvement"
            risk_level = "High Risk"
        student_id = session["student_id"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(""" INSERT INTO predictions (student_id, study_hours, attendance, previous_marks, assignments, sleep_hours, predicted_marks, risk_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?) """, (student_id, study, attendance, previous, assignments, sleep, prediction, risk_level))
        if risk_level == "High Risk":
            cursor.execute(""" INSERT INTO risk_students (student_id, predicted_marks, risk_level) VALUES (?, ?, ?) """, (student_id, prediction, risk_level))
        conn.commit()
        conn.close()
        return render_template("result.html", prediction=round(prediction, 2), category=category, risk=risk_level)
    except Exception as e:
        return f"Error: {e}"

@app.route("/admin")
def admin():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=?", (username,))
        admin = cursor.fetchone()
        conn.close()
        if admin and check_password_hash(admin["password"], password):
            session["admin"] = username
            flash("Login Successful!")
            return redirect("/admin_dashboard")
        flash("Invalid Username or Password")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    try:
        with open("model/model_scores.json", "r") as f:
            scores = json.load(f)
    except:
        scores = {}
    if scores:
        best_model = max(scores, key=scores.get)
        best_score = scores[best_model]
    else:
        best_model = None
        best_score = None
    return render_template("dashboard.html", scores=scores, best_model=best_model, best_score=best_score)

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/login")
    try:
        with open("model/model_scores.json", "r") as f:
            model_scores = json.load(f)
    except:
        model_scores = {}
    try:
        with open("model/feature_importance.json", "r") as f:
            feature_data = json.load(f)
    except:
        feature_data = {}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM risk_students")
    risk_count = cursor.fetchone()[0]
    conn.close()
    return render_template("admin_dashboard.html", model_scores=model_scores, feature_data=feature_data, total_students=total_students, risk_count=risk_count)

@app.route("/admin_predictions")
def admin_predictions():
    if "admin" not in session:
        return redirect("/login")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(""" SELECT predictions.*, students.name, students.email FROM predictions LEFT JOIN students ON predictions.student_id = students.id ORDER BY predictions.id DESC """)
    predictions = cursor.fetchall()
    conn.close()
    return render_template("admin_predictions.html", predictions=predictions)

@app.route("/admin_risk")
def admin_risk():
    if "admin" not in session:
        return redirect("/login")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(""" SELECT risk_students.*, students.name, students.email FROM risk_students LEFT JOIN students ON risk_students.student_id = students.id ORDER BY risk_students.id DESC """)
    risk_students = cursor.fetchall()
    conn.close()
    return render_template("admin_risk.html", risk_students=risk_students)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged Out Successfully!")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
