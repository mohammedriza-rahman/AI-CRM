from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT"))
    SMTP_EMAIL = os.getenv("SMTP_EMAIL")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    IMAP_SERVER = os.getenv("IMAP_SERVER")
    IMAP_PORT = int(os.getenv("IMAP_PORT"))
    IMAP_EMAIL = os.getenv("IMAP_EMAIL")
    IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")

    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

    NEVERBOUNCE_API_KEY = os.getenv("NEVERBOUNCE_API_KEY")

settings = Settings()