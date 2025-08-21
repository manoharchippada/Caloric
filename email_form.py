import datetime
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from jinja2 import Environment, FileSystemLoader
import pytz

# Get today's date as YYYY-MM-DD
tz = pytz.timezone("America/New_York")
today = datetime.now(tz).strftime("%Y-%m-%d")
filename = f"{today}.json"

if not os.path.exists(filename):
    print(f"❌ File {filename} not found.")
    exit(1)

# Load today's nutrition JSON file
with open(filename, "r") as f:
    data = json.load(f)

total_calories = data.get("totalCalories", 0)
target = int(os.getenv("CALORIE_TARGET", 2000))

if total_calories > target:
    sender = os.getenv("EMAIL_SENDER")
    recipient = os.getenv("EMAIL_RECIPIENT")
    app_password = os.getenv("EMAIL_PASSWORD")  # Google App 16-digit password

    # Jinja2 template rendering
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("email_template.html")
    html_content = template.render(
        date=today,
        total_calories=total_calories,
        target=target,
        category_breakdown=data.get("categoryBreakdown", {})
    )

    # Create MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Calorie Alert for {today}"
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, app_password)
            server.send_message(msg)
        print("📧 Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
else:
    print(f"✅ Calories within limit: {total_calories}/{target}")
