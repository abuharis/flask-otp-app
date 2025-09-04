import smtplib
from email.message import EmailMessage

def send_otp(sender_email, smtp_user, smtp_pass, recipient_email, otp_code):
    smtp_server = ""
    smtp_port = 465
    msg = EmailMessage()
    msg.set_content(f"Your OTP is {otp_code}. It will expire in 30 seconds.")
    msg['Subject'] = "Login OTP"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_pass)
            result = smtp.send_message(msg)
            print("send_message result:", result)
            # Even if result is {}, it's still a success
        return True
    except Exception as e:
        import traceback
        print("Error sending OTP:", e)
        traceback.print_exc()
        return False