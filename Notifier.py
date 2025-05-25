import smtplib
from email.mime.text import MIMEText

PREFERRED_CATEGORIES = ["Data Science", "AI", "Machine Learning"]

def alert_user_if_match(df_new):
    matches = df_new[df_new['Skills'].str.contains('|'.join(PREFERRED_CATEGORIES), case=False, na=False)]

    if not matches.empty:
        # Example: print to console (or send email, see below)
        print("New preferred jobs found:")
        print(matches[['Title', 'Company', 'Location', 'Skills']])

        # Optional: Send email
        # send_email_alert(matches)

def send_email_alert(matches):
    sender = "your_email@example.com"
    recipient = "user@example.com"
    subject = "New Jobs Matching Your Preferences"
    body = matches.to_string()

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("your_email@example.com", "your_password")
        server.sendmail(sender, recipient, msg.as_string())
