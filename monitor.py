import psutil
import smtplib
import time
import platform
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (
    CPU_THRESHOLD, MEMORY_THRESHOLD, DISK_THRESHOLD,
    CHECK_INTERVAL_SECONDS, EMAIL_SENDER, EMAIL_PASSWORD,
    EMAIL_RECEIVER, SMTP_HOST, SMTP_PORT, SERVER_NAME
)


def get_system_metrics():
    """Collect current CPU, memory and disk metrics."""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    return cpu, memory, disk


def build_email(cpu, memory, disk, alerts):
    """Build a formatted HTML alert email."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alert_rows = ""
    for alert in alerts:
        alert_rows += f"<tr><td style='padding:8px;color:#c0392b;font-weight:bold;'>{alert}</td></tr>"

    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#c0392b;">🚨 Server Alert — {SERVER_NAME}</h2>
      <p style="color:#555;">Threshold exceeded at <strong>{timestamp}</strong></p>

      <h3 style="color:#333;">Current Metrics</h3>
      <table style="border-collapse:collapse;width:100%;">
        <tr style="background:#f2f2f2;">
          <th style="padding:8px;text-align:left;">Metric</th>
          <th style="padding:8px;text-align:left;">Value</th>
          <th style="padding:8px;text-align:left;">Threshold</th>
          <th style="padding:8px;text-align:left;">Status</th>
        </tr>
        <tr>
          <td style="padding:8px;">CPU Usage</td>
          <td style="padding:8px;"><strong>{cpu}%</strong></td>
          <td style="padding:8px;">{CPU_THRESHOLD}%</td>
          <td style="padding:8px;">{'🔴 ALERT' if cpu >= CPU_THRESHOLD else '🟢 OK'}</td>
        </tr>
        <tr style="background:#f9f9f9;">
          <td style="padding:8px;">Memory Usage</td>
          <td style="padding:8px;"><strong>{memory}%</strong></td>
          <td style="padding:8px;">{MEMORY_THRESHOLD}%</td>
          <td style="padding:8px;">{'🔴 ALERT' if memory >= MEMORY_THRESHOLD else '🟢 OK'}</td>
        </tr>
        <tr>
          <td style="padding:8px;">Disk Usage</td>
          <td style="padding:8px;"><strong>{disk}%</strong></td>
          <td style="padding:8px;">{DISK_THRESHOLD}%</td>
          <td style="padding:8px;">{'🔴 ALERT' if disk >= DISK_THRESHOLD else '🟢 OK'}</td>
        </tr>
      </table>

      <h3 style="color:#c0392b;">Alerts Triggered</h3>
      <table style="border-collapse:collapse;width:100%;">
        {alert_rows}
      </table>

      <hr style="margin-top:20px;"/>
      <p style="color:#aaa;font-size:12px;">
        Server: {SERVER_NAME} | OS: {platform.system()} {platform.release()} | 
        Sent by server-health-monitor
      </p>
    </body></html>
    """
    return html


def send_alert(cpu, memory, disk, alerts):
    """Send alert email via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 Alert: {SERVER_NAME} — {', '.join(alerts)}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    html_body = build_email(cpu, memory, disk, alerts)
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Alert email sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to send email: {e}")


def check_and_alert(cpu, memory, disk):
    """Compare metrics against thresholds and trigger alert if needed."""
    alerts = []
    if cpu >= CPU_THRESHOLD:
        alerts.append(f"CPU at {cpu}% (threshold: {CPU_THRESHOLD}%)")
    if memory >= MEMORY_THRESHOLD:
        alerts.append(f"Memory at {memory}% (threshold: {MEMORY_THRESHOLD}%)")
    if disk >= DISK_THRESHOLD:
        alerts.append(f"Disk at {disk}% (threshold: {DISK_THRESHOLD}%)")

    if alerts:
        send_alert(cpu, memory, disk, alerts)
    return alerts


def main():
    print(f"🖥️  Server Health Monitor started for: {SERVER_NAME}")
    print(f"📊 Thresholds — CPU: {CPU_THRESHOLD}% | Memory: {MEMORY_THRESHOLD}% | Disk: {DISK_THRESHOLD}%")
    print(f"⏱️  Checking every {CHECK_INTERVAL_SECONDS} seconds\n")

    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        cpu, memory, disk = get_system_metrics()

        print(f"[{timestamp}] CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%", end="")

        alerts = check_and_alert(cpu, memory, disk)
        if not alerts:
            print(" — ✅ All OK")
        else:
            print(f" — 🚨 {len(alerts)} alert(s) sent")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
