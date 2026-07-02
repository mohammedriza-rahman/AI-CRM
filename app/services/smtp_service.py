import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

logger = logging.getLogger(__name__)


class SMTPService:

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.email = settings.SMTP_EMAIL
        self.password = settings.SMTP_PASSWORD

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str
    ):

        try:

            message = MIMEMultipart()

            message["From"] = self.email
            message["To"] = recipient
            message["Subject"] = subject

            message.attach(
                MIMEText(body, "plain")
            )

            context = ssl.create_default_context()

            with smtplib.SMTP(
                self.smtp_server,
                self.smtp_port
            ) as server:

                server.starttls(context=context)

                server.login(
                    self.email,
                    self.password
                )

                server.sendmail(
                    self.email,
                    recipient,
                    message.as_string()
                )

            logger.info(
                f"Email sent to {recipient}"
            )

            return True

        except Exception as e:

            logger.error(e)

            return False