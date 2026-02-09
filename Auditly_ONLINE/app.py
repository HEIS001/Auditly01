from flask import Flask, render_template, request, redirect, session
import sqlite3, uuid, os, smtplib, requests
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "auditly-secret"
DB = "auditly.db"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
BASE_URL = "https://yourdomain.com"

def get_db():
    return sqlite3.connect(DB)

# --- Email verification ---
def send_verification_email(email, token):
    msg = EmailMessage()
    msg['Subject'] = 'Verify your Auditly account'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    link = f"{BASE_URL}/verify/{token}"
    msg.set_content(f"Click to verify: {link}")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]
        token = str(uuid.uuid4())
        db = get_db()
        db.execute("INSERT INTO users(email,password,verify_token) VALUES(?,?,?)", (email,password,token))
        db.commit()
        db.close()
        send_verification_email(email, token)
        return "Account created. Check email to verify."
    return render_template("signup.html")

@app.route("/verify/<token>")
def verify(token):
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE verify_token=?", (token,)).fetchone()
    if not user:
        return "Invalid token"
    db.execute("UPDATE users SET verify_token=NULL, is_verified=1 WHERE id=?", (user[0],))
    db.commit()
    db.close()
    return "Email verified. You can login."

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT id,is_verified FROM users WHERE email=? AND password=?", (email,password)).fetchone()
        db.close()
        if not user:
            return "Invalid credentials"
        if user[1]==0:
            return "Please verify your email first"
        session["user_id"] = user[0]
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "user_id" not in session:
        return redirect("/login")
    file = request.files["file"]
    file.save("uploads/" + file.filename)
    return "File uploaded. AI will process it."

# --- Admin ---
@app.route("/admin")
def admin():
    db = get_db()
    users = db.execute("SELECT email, plan FROM users").fetchall()
    db.close()
    return render_template("admin.html", users=users)

if __name__=="__main__":
    app.run(debug=True)
