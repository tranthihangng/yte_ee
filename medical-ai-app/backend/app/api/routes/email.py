import smtplib
import json
from email.message import EmailMessage

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings

router = APIRouter()


@router.post("/send-report-email")
async def send_report_email(
    to_email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(""),
    case_id: int = Form(...),
    attachment_types: str = Form(default="[]"),
    attachments: list[UploadFile] = File(default=[]),
):
    if "@" not in to_email or "." not in to_email:
        raise HTTPException(status_code=400, detail="Invalid recipient email")
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        raise HTTPException(
            status_code=500,
            detail="SMTP is not configured. Set SMTP_HOST/SMTP_USER/SMTP_PASSWORD in backend .env",
        )

    if not attachments:
        raise HTTPException(status_code=400, detail="No attachments provided")

    try:
        requested_types = json.loads(attachment_types)
    except json.JSONDecodeError:
        requested_types = []
    if not isinstance(requested_types, list):
        requested_types = []

    try:
        email = EmailMessage()
        email["Subject"] = subject
        email["From"] = settings.smtp_from_email or settings.smtp_user
        email["To"] = to_email
        base_message = message or f"Bao cao cho ca benh {case_id} tu MedAI Assist."
        if requested_types:
            base_message = base_message + f"\n\nAttachments: {', '.join(requested_types)}"
        email.set_content(base_message)

        for idx, upload in enumerate(attachments):
            attachment_bytes = await upload.read()
            attachment_name = upload.filename or f"report_{case_id}_{idx}"
            maintype = "application"
            subtype = "octet-stream"
            lower_name = attachment_name.lower()
            if lower_name.endswith(".pdf"):
                maintype, subtype = "application", "pdf"
            elif lower_name.endswith(".png"):
                maintype, subtype = "image", "png"
            elif lower_name.endswith(".jpg") or lower_name.endswith(".jpeg"):
                maintype, subtype = "image", "jpeg"
            email.add_attachment(attachment_bytes, maintype=maintype, subtype=subtype, filename=attachment_name)

        smtp_user = settings.smtp_user.strip()
        smtp_password = settings.smtp_password.replace(" ", "").strip()
        from_email = (settings.smtp_from_email or smtp_user).strip()
        email.replace_header("From", from_email)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=25) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(email)
    except smtplib.SMTPAuthenticationError as exc:
        raise HTTPException(status_code=401, detail="SMTP authentication failed. Check SMTP_USER/SMTP_PASSWORD") from exc
    except smtplib.SMTPException as exc:
        raise HTTPException(status_code=502, detail=f"Email server error: {exc}") from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail="Email sending timeout") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {exc}") from exc

    return {"status": "ok", "message": f"Report sent to {to_email}"}
