from flask import Flask, render_template, jsonify, request ,session, redirect
import sqlite3 
import hashlib
app = Flask(__name__)
app.secret_key = "panda"
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            bio TEXT,
            notifications INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    
@app.route("/")
def home():
    return render_template("index.html")
#registration page
@app.route("/register")
def register():
    return render_template("register.html")

# Registration Route
@app.route("/register_user", methods=["POST"])
def register_user():
    data = request.get_json()  # Accept JSON
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    # Validate required fields
    if not all([name, email, phone, username, password, role]):
        return jsonify({"success": False, "error": "All fields are required!"})

    hashed_password = hash_password(password)

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO users (name, email, phone, username, password, role)
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                          (name, email, phone, username, hashed_password, role))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Registration successful!"})

    except sqlite3.IntegrityError as e:
        error_msg = "Email or Username already registered!"
        return jsonify({"success": False, "error": error_msg}) 
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")
from flask import session

@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "error": "All fields are required!"})
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, stored_password = user
        if hash_password(password) == stored_password:
            session["user_id"] = user_id
            session["username"] = username
            return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid username or password!"})

@app.route('/save_profile', methods=['POST'])
def save_profile():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "User not logged in"})

    data = request.get_json()
    full_name = data.get("fullName")
    email = data.get("email")
    phone = data.get("phone")
    location = data.get("location")
    bio = data.get("bio")
    account_type = data.get("accountType")
    notifications = data.get("notifications", False)

    if not (full_name and email and phone and location):
        return jsonify({"success": False, "error": "All fields are required"})

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET full_name = ?, email = ?, phone = ?, location = ?, bio = ?, account_type = ?, notifications = ?
        WHERE id = ?
    """, (full_name, email, phone, location, bio, account_type, int(notifications), session["user_id"]))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Profile updated successfully"})


@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")
@app.route("/help")
def help_page(): 
    return render_template("help.html")
@app.route("/forgetpass")
def forget_pass(): 
    return render_template("forgetpass.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route('/profile')
def profile():
    return render_template('profile.html')
@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect("/login")  
    return render_template('dashboard.html', username=session['username'])



if __name__ == "__main__":
    init_db()
    app.run(debug=True)
