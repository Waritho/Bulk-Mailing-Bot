import csv
import json
import time
import smtplib
import os
import re
from email.utils import formataddr
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

CONFIG_PATH = 'config.json'
EMAILS_PATH = 'emails.csv'
RESUME_PATH = 'Shubh_Agrawal_Resume.pdf'
SEND_DELAY = 1

def is_valid_email(email):
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", email)

# 1. Load config
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

SMTP_SERVER = config['smtp_server']
SMTP_PORT = config.get('smtp_port', 465)
SENDER_EMAIL = config['email']
SENDER_PASS = config['password']
SENDER_NAME = config.get('name', "Your Name")

# 2. Load recipients
recipients = []
with open(EMAILS_PATH, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if not row or not row[0].strip():
            continue
        if i == 0 and 'email' in row[0].lower():
            continue
        email_addr = row[0].strip()
        if is_valid_email(email_addr):
            recipients.append(email_addr)
        else:
            print(f"Skipping invalid email: {email_addr}")

# 3. Send loop
for to_email in recipients:
    msg = MIMEMultipart('mixed')  # For attachments
    msg['From'] = formataddr((str(Header(SENDER_NAME, 'utf-8')), SENDER_EMAIL))
    msg['To'] = to_email
    msg['Subject'] = f"Resume of {SENDER_NAME} - Application for Opportunities"
    msg['List-Unsubscribe'] = '<mailto:unsubscribe@yourdomain.com>'

    # -- Text part: Short fallback --
    text_body = (
        "Resume attached.\n\n"
        f"Best regards,\n{SENDER_NAME}"
    )

    # -- HTML part: Full styled content --
    html_body = f"""\
   <html>
  <body style="font-family:Arial,sans-serif;font-size:15px;">
    <p>
      Dear Sir/Madam,
    </p>
    <p>
      I hope this email finds you well.
    </p>
    <p>
      My name is {SENDER_NAME}, and I am actively seeking entry-level opportunities in the technology sector. I am particularly drawn to mainstream technical roles and possess hands-on experience working with large language model systems. My area of focus is prompt engineering, which enables me to design, optimize, and deploy advanced AI-driven solutions.
    </p>
    <p>
      I am passionate about building impactful technologies and collaborating with innovative teams. I have attached my resume for your review, providing further insight into my skills and professional background.
    </p>
    <p>
      I would be sincerely grateful if you could consider referring me within your company or organization for any suitable entry-level positions that match my qualifications and interests. Your referral or any guidance you could offer would be greatly appreciated and would help me take the next step in my tech career.
    </p>
    <p>
      Thank you very much for your time and consideration.<br>
      I look forward to the opportunity to contribute my enthusiasm and expertise to your organization.
    </p>
    <p>
      Best regards,<br>
      {SENDER_NAME}
    </p>
  </body>
</html>
    """

    # Bundle text & HTML alternative
    alternative = MIMEMultipart('alternative')
    alternative.attach(MIMEText(text_body, 'plain', 'utf-8'))
    alternative.attach(MIMEText(html_body, 'html', 'utf-8'))
    msg.attach(alternative)

    # PDF attachment
    if os.path.exists(RESUME_PATH):
        with open(RESUME_PATH, "rb") as f:
            pdf = MIMEApplication(f.read(), _subtype="pdf")
            pdf.add_header('Content-Disposition', 'attachment', filename=os.path.basename(RESUME_PATH))
            msg.attach(pdf)
    else:
        print(f"ERROR: Resume '{RESUME_PATH}' not found. Skipping email to {to_email}.")
        continue

    # Send
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        print(f"Sent to {to_email}")
    except Exception as e:
        print(f"Failed to send to {to_email}: {e}")

    time.sleep(SEND_DELAY)

print("All emails processed.")
