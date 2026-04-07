import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecret"
DB = "gym.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Admin table
    c.execute("""CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT
                )""")
    # Members table
    c.execute("""CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    photo TEXT
                )""")
    # Workouts table
    c.execute("""CREATE TABLE IF NOT EXISTS workouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    image TEXT
                )""")
    # Add default admin
    c.execute("INSERT OR IGNORE INTO admin (id, username, password) VALUES (1, 'admin', 'admin')")
    conn.commit()
    conn.close()

init_db()

# Allowed file check
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        admin = c.fetchone()
        conn.close()
        if admin:
            session["admin"] = username
            return redirect("/dashboard")
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM members")
    members = c.fetchall()
    conn.close()
    return render_template("dashboard.html", members=members)

@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if "admin" not in session:
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        photo = request.files["photo"]
        filename = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO members (name, age, photo) VALUES (?, ?, ?)", (name, age, filename))
        conn.commit()
        conn.close()
        return redirect("/dashboard")
    return render_template("add_member.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)