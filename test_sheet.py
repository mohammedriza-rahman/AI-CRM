from app.services.google_sheet_service import GoogleSheetService

if __name__ == "__main__":
    print("Testing Google Sheets Connection...")
    service = GoogleSheetService()
    
    # 1. Test Reading
    pending = service.get_pending_leads()
    print(f"Found pending leads: {pending}")
    
    # 2. Test Updating
    if pending:
        print("Updating status to 'Processing' for the first lead...")
        # Index 0 means row 2 in the sheet
        service.update_lead_cell(row_index=0, column_name="Processing Status", value="Processing")
        print("Done! Check your browser to see if the sheet updated live.")