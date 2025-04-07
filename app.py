from flask import Flask, render_template, jsonify, request
import sqlite3
import hashlib

app = Flask(__name__)

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# How It Works page
@app.route("/howitworks")
def how_it_works():
    return render_template("howitworks.html")

# Help page
@app.route("/help")
def help_page():
    return render_template("help.html")

# About page
@app.route("/about")
def about():
    return render_template("about.html")

# Registration route
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"success": False, "error": "All fields are required!"})

    hashed_password = hash_password(password)

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                       (name, email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Registration successful!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Email already registered!"})

# Login route
@app.route("/login_user", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"})

    hashed_password = hash_password(password)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ? AND password = ?", (email, hashed_password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "user_id": user[0]})
    else:
        return jsonify({"success": False, "error": "Invalid credentials"})

# Run the app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
