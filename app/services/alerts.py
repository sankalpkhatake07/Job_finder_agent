import smtplib
from email.message import EmailMessage
import httpx
from sqlalchemy import select
from ..config import settings
from ..models import AlertLog

def _text(job, score):
    return (f"🔥 {score.category} MATCH — {score.final_score:.1f}%\n\n"
            f"{job.title}\n{job.company}\n{job.location or 'Location not listed'}\n\n"
            f"Matched: {', '.join(score.matched_skills[:12]) or 'None'}\n"
            f"Missing: {', '.join(score.missing_skills[:8]) or 'None'}\n\n"
            f"{score.explanation}\n\nApply: {job.url}")

def send_telegram(db, job, score):
    if not settings.telegram_bot_token or not settings.telegram_chat_id: return False
    r = httpx.post(f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage", data={"chat_id": settings.telegram_chat_id, "text": _text(job, score), "disable_web_page_preview": True}, timeout=20)
    ok = r.is_success
    db.add(AlertLog(job_id=job.id, channel="telegram", status="sent" if ok else "failed", detail=r.text[:1000]))
    db.commit()
    return ok

def send_email(db, job, score):
    if not all([settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.alert_email_to]): return False
    msg = EmailMessage(); msg["Subject"] = f"[{score.category} {score.final_score:.0f}%] {job.title} — {job.company}"; msg["From"] = settings.smtp_username; msg["To"] = settings.alert_email_to; msg.set_content(_text(job, score))
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls(); server.login(settings.smtp_username, settings.smtp_password); server.send_message(msg)
        db.add(AlertLog(job_id=job.id, channel="email", status="sent")); db.commit(); return True
    except Exception as e:
        db.add(AlertLog(job_id=job.id, channel="email", status="failed", detail=str(e))); db.commit(); return False
