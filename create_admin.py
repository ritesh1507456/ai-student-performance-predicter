# ADMIN SCRIPT (PRODUCTION VERSION)

import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "database.db"

def create_admin(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    cursor.execute("""
        INSERT OR IGNORE INTO admin (username, password)
        VALUES (?, ?)
    """, (username, hashed_password))

    conn.commit()
    conn.close()

    print("✅ Admin Created Successfully!")

if __name__ == "__main__":
    print("Creating Default Admin...\n")
    create_admin("admin", "admin123")