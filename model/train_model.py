# IMPORT LIBRARIES

import pandas as pd
import numpy as np
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from datetime import datetime

# CREATE REQUIRED DIRECTORIES

os.makedirs("model", exist_ok=True)
os.makedirs("static/charts", exist_ok=True)

try:
    data = pd.read_excel("dataset/student_data.xlsx")
    print("✅ Dataset Loaded Successfully!\n")
except Exception as e:
    print("❌ Error Loading Dataset:", e)
    exit()

required_columns = [
    'Study_Hours',
    'Attendance',
    'Previous_Marks',
    'Assignments',
    'Sleep_Hours',
    'Final_Marks'
]

for col in required_columns:
    if col not in data.columns:
        print(f"❌ Missing Column: {col}")
        exit()


features = [
    'Study_Hours',
    'Attendance',
    'Previous_Marks',
    'Assignments',
    'Sleep_Hours'
]

X = data[features]
y = data['Final_Marks']


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# INITIALIZE MODELS

models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(random_state=42)
}

scores = {}

print("🔎 Training Models...\n")

for name, model in models.items():
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    scores[name] = score
    print(f"{name}: {round(score,4)}")

best_model_name = max(scores, key=scores.get)
best_model = models[best_model_name]

print(f"\n🏆 Best Model Selected: {best_model_name}")

joblib.dump(best_model, "model/model.pkl")
joblib.dump(scaler, "model/scaler.pkl")

print("✅ Model & Scaler Saved Successfully!")

with open("model/model_scores.json", "w") as f:
    json.dump(scores, f, indent=4)

print("✅ Model Scores Saved!")

if best_model_name == "Random Forest":
    importances = best_model.feature_importances_
    feature_data = dict(zip(features, importances))

    with open("model/feature_importance.json", "w") as f:
        json.dump(feature_data, f, indent=4)

    print("✅ Feature Importance Saved!")

print("\n📊 Generating Analytics Graphs...")

# Feature Importance
if best_model_name == "Random Forest":
    plt.figure(figsize=(8,5))
    plt.bar(features, importances)
    plt.title("Feature Importance")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/charts/feature_importance.png")
    plt.close()

# Correlation Heatmap
plt.figure(figsize=(8,6))
sns.heatmap(data.corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig("static/charts/heatmap.png")
plt.close()

# Marks Distribution
plt.figure(figsize=(8,5))
plt.hist(y, bins=6)
plt.title("Final Marks Distribution")
plt.xlabel("Marks")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.savefig("static/charts/distribution.png")
plt.close()

print("✅ Graphs Generated Successfully!")

try:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO model_logs (model_name, accuracy)
        VALUES (?, ?)
    """, (best_model_name, scores[best_model_name]))

    conn.commit()
    conn.close()

    print("✅ Model Training Logged in Database!")

except:
    print("⚠ Database Logging Skipped (Run setup_database.py first)")

print("\n🎉 MODEL TRAINING COMPLETED SUCCESSFULLY!")
print("System Ready for Deployment 🚀")