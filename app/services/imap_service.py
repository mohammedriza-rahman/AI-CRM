import imaplib
import email
from email.header import decode_header
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class IMAPService:

    def __init__(self):

        self.server = settings.IMAP_SERVER
        self.port = settings.IMAP_PORT
        self.username = settings.IMAP_EMAIL
        self.password = settings.IMAP_PASSWORD

    def connect(self):

        mail = imaplib.IMAP4_SSL(
            self.server,
            self.port
        )

        mail.login(
            self.username,
            self.password
        )

        return mail

    def get_unread_emails(self):

        mail = self.connect()

        mail.select("INBOX")

        status, messages = mail.search(
            None,
            'UNSEEN'
        )

        email_ids = messages[0].split()

        results = []

        for email_id in email_ids:

            status, msg_data = mail.fetch(
                email_id,
                "(RFC822)"
            )

            raw_email = msg_data[0][1]

            message = email.message_from_bytes(
                raw_email
            )

            sender = message.get("From")

            subject = decode_header(
                message["Subject"]
            )[0][0]

            if isinstance(subject, bytes):
                subject = subject.decode()

            body = ""

            if message.is_multipart():

                for part in message.walk():

                    content_type = part.get_content_type()

                    disposition = str(
                        part.get("Content-Disposition")
                    )

                    if (
                        content_type == "text/plain"
                        and "attachment" not in disposition
                    ):

                        body = part.get_payload(
                            decode=True
                        ).decode()

                        break

            else:

                body = message.get_payload(
                    decode=True
                ).decode()

            results.append({

                "sender": sender,

                "subject": subject,

                "body": body

            })

        mail.logout()

        return results