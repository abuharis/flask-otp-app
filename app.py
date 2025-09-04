from flask import Flask, request, jsonify, redirect, url_for, render_template, flash, session
from email_utils import send_otp
import random
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# --- Configuration ---
SENDER_EMAIL = ""
SMTP_USER = ""
SMTP_PASS = ""

# --- Database Setup ---
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_FILE = "database.db"
app.secret_key = "supersecret"  # for session and flash

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            otp_code TEXT,
            otp_expiry DATETIME
        )
    """)

    # Create posts table`
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        image_path TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Create likes table
    c.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, post_id),
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(post_id) REFERENCES posts(id)
    )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Generate Random OTP ---
def generate_otp(length=6):
    return ''.join([str(random.randint(0,9)) for _ in range(length)])

@app.route("/")
def home():
    return redirect(url_for("register"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email) VALUES (?)", (email,))
            conn.commit()
            flash("Registration successful. Please log in.", "success")
        except sqlite3.IntegrityError:
            flash("Email already registered.", "danger")
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]

        otp_code = generate_otp()
        otp_expiry = int((datetime.now() + timedelta(seconds=30)).timestamp())

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET otp_code=?, otp_expiry=? WHERE email=?", (otp_code, otp_expiry, email))
        conn.commit()
        conn.close()

        success = send_otp(SENDER_EMAIL, SMTP_USER, SMTP_PASS, email, otp_code)
        if success:
            flash("OTP sent to your email.", "info")
            session["email"] = email
            
            return redirect(url_for("verify"))
        else:
            flash("Failed to send OTP.", "danger")
    return render_template("login.html")

# --- OTP Endpoint ---
@app.route("/send_otp", methods=["POST"])
def send_otp_endpoint():
    data = request.json
    user_email = data.get("email")
    if not user_email:
        return jsonify({"error": "Email is required"}), 400

    otp_code = generate_otp()
    otp_expiry = int((datetime.now() + timedelta(seconds=30)).timestamp())

    # Save OTP in SQLite
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO users (email, otp_code, otp_expiry)
        VALUES (?, ?, ?)
    """, (user_email, otp_code, otp_expiry))
    conn.commit()
    conn.close()

    # Send OTP via SES
    success = send_otp(SENDER_EMAIL, SMTP_USER, SMTP_PASS, user_email, otp_code)
    print(success)
    if success:
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send OTP"}), 500
    
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        email = session.get("email")
        otp_input = request.form["otp"]

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT otp_code, otp_expiry FROM users WHERE email=?", (email,))
        row = c.fetchone()

        if not row:
            flash("User not found.", "danger")
            return redirect(url_for("login"))

        otp_code, otp_expiry = row
        now = int(datetime.now().timestamp())

        if otp_input == otp_code and now < int(otp_expiry):
            c.execute("SELECT id FROM users WHERE email = ?", (email,))
            row = c.fetchone()
            conn.close()   # Useful for leanring purpose. This single line placement is very important

            user_id = row[0]

            session["user_id"] = user_id
            session["email"] = email

            print(session["user_id"] , session["email"])

            flash("Login successful!", "success")
            return render_template("feed.html", email=email)
        else:
            flash("Invalid or expired OTP.", "danger")
            return redirect(url_for("login"))

    return render_template("verify.html")

# ===================
# POSTS & LIKES
# ===================

@app.route("/feed")
def feed():
    # if "user_id" not in session:
    #     return redirect(url_for("login"))

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT posts.id, posts.content, posts.image_path, users.email,
               (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) as like_count,
               EXISTS(SELECT 1 FROM likes WHERE likes.post_id = posts.id AND likes.user_id = ?) as liked
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """, (session["user_id"],))
    posts = c.fetchall()
    conn.close()

    return render_template("feed.html", posts=posts)


@app.route("/create_post", methods=["POST"])
def create_post():
    # if "user_id" not in session:
    #     return redirect(url_for("login"))

    content = request.form["content"]
    image = request.files.get("image")

    image_path = None
    if image and image.filename:
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO posts (user_id, content, image_path) VALUES (?, ?, ?)",
              (session["user_id"], content, image_path))
    conn.commit()
    conn.close()

    flash("Post created!", "success")
    return redirect(url_for("feed"))


@app.route("/like/<int:post_id>")
def like(post_id):
    # if "user_id" not in session:
    #     return redirect(url_for("login"))

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", (session["user_id"], post_id))
        conn.commit()
    except sqlite3.IntegrityError:
        # User already liked → unlike
        c.execute("DELETE FROM likes WHERE user_id=? AND post_id=?", (session["user_id"], post_id))
        conn.commit()
    conn.close()

    return redirect(url_for("feed"))


# --- Run Flask ---
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)