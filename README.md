# 📌 Flask OTP Authentication App

A simple Flask-based web application that allows:  
- User registration with email  
- OTP-based login (sent via AWS SES SMTP server)  
- Create text/image posts  
- Like/unlike posts  
- SQLite database for persistence  

---

## 🚀 Features
- OTP login with expiry (30 seconds default)  
- Session-based authentication  
- Post creation (text required, image optional)  
- Like/unlike system with unique constraints  
- SQLite for lightweight storage  

---

## 📂 Project Structure
flask-otp-app/
│── app.py # Main Flask app
│── email_utils.py # Email sending logic (SMTP)
│── requirements.txt # Dependencies
│── templates/ # HTML templates
│── static/ # CSS, JS, images
│── database.db # SQLite DB (created at runtime)
│── venv/ # Virtual environment (ignored in git)


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repo
```bash
git clone https://github.com/<your-username>/flask-otp-app.git
cd flask-otp-app
```

### 2️⃣ Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure SMTP (AWS SES in this example)
#### - In email_utils.py, set your SES endpoint:
```bash
smtp_server = "email-smtp.ap-south-1.amazonaws.com"
```

#### - In app.py, configure credentials:
```bash
SENDER_EMAIL = "your-verified-email@example.com"
SMTP_USER = "your-smtp-username"
SMTP_PASS = "your-smtp-password"
```

#### ⚠️ Security tip: Do NOT hardcode secrets in production.
#### Use environment variables (os.environ) or a .env file.

### 5️⃣ Run the app
```bash
python app.py
```

# 📌 Requirements
See `requirements.txt`

# 🙌 Contribution
### Feel free to fork, improve, and PR.




