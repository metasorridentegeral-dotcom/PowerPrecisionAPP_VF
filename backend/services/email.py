"""
Email Service - Sends real emails via SMTP SSL
"""
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# SMTP Configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")


def is_smtp_configured() -> bool:
    """Check if SMTP is properly configured"""
    return all([SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD])


async def send_email_notification(to_email: str, subject: str, body: str, html_body: str = None) -> bool:
    """
    Send email notification via SMTP SSL
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body
    
    Returns:
        True if email sent successfully, False otherwise
    """
    if not is_smtp_configured():
        print(f"[EMAIL SIMULATED] SMTP not configured")
        print(f"  To: {to_email}")
        print(f"  Subject: {subject}")
        print(f"  Body: {body[:100]}...")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Power Real Estate & Precision <{SMTP_EMAIL}>"
        msg["To"] = to_email
        
        # Add plain text part
        part1 = MIMEText(body, "plain", "utf-8")
        msg.attach(part1)
        
        # Add HTML part if provided
        if html_body:
            part2 = MIMEText(html_body, "html", "utf-8")
            msg.attach(part2)
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and send
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        
        print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
        return True
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {str(e)}")
        return False


async def send_new_client_notification(
    client_name: str,
    client_email: str,
    client_phone: str,
    process_type: str,
    staff_email: str,
    staff_name: str
) -> bool:
    """Send notification to staff member about new client registration"""
    
    subject = f"Novo Cliente Registado: {client_name}"
    
    body = f"""
Olá {staff_name},

Foi registado um novo cliente que lhe foi atribuído:

Nome: {client_name}
Email: {client_email}
Telefone: {client_phone}
Tipo de Processo: {process_type}

Aceda à plataforma para ver todos os detalhes.

Cumprimentos,
Power Real Estate & Precision
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1F845A 0%, #3FA495 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; }}
        .client-info {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        .label {{ font-weight: bold; color: #666; }}
        .footer {{ text-align: center; padding: 15px; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin: 0;">🏠 Novo Cliente Registado</h2>
        </div>
        <div class="content">
            <p>Olá <strong>{staff_name}</strong>,</p>
            <p>Foi registado um novo cliente que lhe foi atribuído:</p>
            
            <div class="client-info">
                <p><span class="label">Nome:</span> {client_name}</p>
                <p><span class="label">Email:</span> <a href="mailto:{client_email}">{client_email}</a></p>
                <p><span class="label">Telefone:</span> {client_phone}</p>
                <p><span class="label">Tipo de Processo:</span> {process_type}</p>
            </div>
            
            <p>Aceda à plataforma para ver todos os detalhes do cliente.</p>
        </div>
        <div class="footer">
            <p>Power Real Estate & Precision</p>
        </div>
    </div>
</body>
</html>
"""
    
    return await send_email_notification(staff_email, subject, body, html_body)


async def send_status_update_notification(
    client_email: str,
    client_name: str,
    new_status: str,
    message: str = ""
) -> bool:
    """Send notification to client about status update"""
    
    subject = f"Atualização do seu processo - {new_status}"
    
    body = f"""
Olá {client_name},

O estado do seu processo foi atualizado para: {new_status}

{message}

Para mais informações, entre em contacto connosco.

Cumprimentos,
Power Real Estate & Precision
"""
    
    return await send_email_notification(client_email, subject, body)
