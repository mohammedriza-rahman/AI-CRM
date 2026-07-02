import logging
from app.services.google_sheet_service import GoogleSheetService
from app.graph.workflow import run_workflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

if __name__ == "__main__":
    print("Testing CRM Workflow...")
    service = GoogleSheetService()
    leads = service.get_pending_leads()
    print(f"Found {len(leads)} pending leads.")
    if leads:
        lead = leads[0]
        print(f"Processing first lead: {lead.get('Lead Name')}")
        # Update status to 'Processing' in sheet
        service.update_by_lead_id(lead["Lead ID"], "Processing Status", "Processing")
        # Run workflow
        result = run_workflow(lead)
        print("Workflow finished successfully!")
        print("Result:")
        import pprint
        pprint.pprint(result)
    else:
        print("No pending leads found to test workflow. Please reset a lead's Processing Status to 'Pending' in your Google Sheet.")
