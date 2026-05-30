# Alert thresholds (percentage)
CPU_THRESHOLD = 80       # Alert if CPU usage exceeds 80%
MEMORY_THRESHOLD = 80    # Alert if memory usage exceeds 80%
DISK_THRESHOLD = 85      # Alert if disk usage exceeds 85%

# Monitoring interval
CHECK_INTERVAL_SECONDS = 60  # Check every 60 seconds

# Email configuration (values loaded from .env file)
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")       # Your Gmail address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")   # Your Gmail App Password
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")   # Where alerts get sent (can be same address)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Server name (shows up in alert emails)
SERVER_NAME = os.getenv("SERVER_NAME", "my-linux-server")
