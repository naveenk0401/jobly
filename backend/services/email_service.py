import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import settings

def _get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=settings.GMAIL_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/gmail.send"]
    )
    return build("gmail", "v1", credentials=creds)

async def send_application_email(
    to_email: str,
    user_name: str,
    job_title: str,
    company: str,
    job_url: str,
    score: float,
) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Applied: {job_title} at {company}"
        msg["From"]    = settings.GMAIL_SENDER
        msg["To"]      = to_email

        html = f"""
        <div style="font-family:sans-serif;max-width:540px;
                    margin:0 auto;padding:32px 24px">
          <h2 style="margin:0 0 6px;font-size:20px">
            Application sent
          </h2>
          <p style="color:#666;margin:0 0 24px;font-size:14px">
            Jobly autopilot just applied to a new job for you.
          </p>
          <div style="background:#f7f7f5;border-radius:10px;
                      padding:18px;margin-bottom:20px">
            <p style="margin:0 0 4px;font-weight:500;font-size:16px">
              {job_title}
            </p>
            <p style="margin:0 0 14px;color:#666;font-size:14px">
              {company}
            </p>
            <span style="background:#e1f5ee;color:#085041;
                         padding:4px 12px;border-radius:20px;
                         font-size:13px;font-weight:500">
              {score:.0f}% match
            </span>
          </div>
          <a href="{job_url}"
             style="color:#1D9E75;font-size:14px">
            View job posting →
          </a>
          <p style="color:#bbb;font-size:12px;margin-top:32px">
            Sent by Jobly autopilot. 
            <a href="#" style="color:#bbb">Pause autopilot</a>
          </p>
        </div>
        """

        msg.attach(MIMEText(html, "html"))

        raw = base64.urlsafe_b64encode(
            msg.as_bytes()
        ).decode("utf-8")

        service = _get_gmail_service()
        service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        return True

    except Exception as e:
        print(f"[Email] Failed: {e}")
        return False
