import gspread
from google.oauth2.service_account import Credentials
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class GoogleSheetService:
    def __init__(self):
        # Define the scope needed for Sheets and Drive
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.client = self._authenticate()
        self.sheet = self._open_spreadsheet()

    def _authenticate(self):
        try:
            # Looks for credentials.json in your root directory
            credentials = Credentials.from_service_account_file(
                "credentials.json", 
                scopes=self.scopes
            )
            return gspread.authorize(credentials)
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Cloud: {e}")
            raise e

    def _open_spreadsheet(self):
        try:
            # Opens the sheet named 'Leads' (from your config/env settings)
            return self.client.open(settings.GOOGLE_SHEET_NAME).sheet1
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet '{settings.GOOGLE_SHEET_NAME}' not found. Check the name and sharing permissions.")
            raise
        except Exception as e:
            logger.error(f"Error opening spreadsheet: {e}")
            raise

    def get_all_leads(self):
        """Fetches all rows from the spreadsheet as a list of dictionaries."""
        return self.sheet.get_all_records()

    def get_pending_leads(self):
        """Filters and returns only rows where 'Processing Status' is 'Pending'."""
        all_leads = self.get_all_leads()
        return [lead for lead in all_leads if lead.get("Processing Status") == "Pending"]

    def update_lead_cell(self, row_index: int, column_name: str, value):
        """Updates a single cell based on the row index and column header name."""
        try:
            # Find the column index based on header name
            headers = self.sheet.row_values(1)
            if column_name not in headers:
                logger.error(f"Column '{column_name}' not found in headers.")
                return False
            
            col_index = headers.index(column_name) + 1
            # row_index + 2 because rows are 1-indexed and row 1 is the header
            self.sheet.update_cell(row_index + 2, col_index, str(value))
            return True
        except Exception as e:
            logger.error(f"Failed to update cell: {e}")
            return False