import datetime
import logging
from pathlib import Path

from app.services.gemini_service import GeminiService
from app.services.google_sheet_service import GoogleSheetService
from app.services.smtp_service import SMTPService

logger = logging.getLogger(__name__)


class ReportGenerator:

    def __init__(self):

        self.llm = GeminiService()

        self.sheet = GoogleSheetService()

        self.smtp = SMTPService()

    def run(self, state):

        # Keep compatibility with single-lead run if needed
        lead = state.get("lead")
        verification = state.get("verification")
        classification = state.get("classification")

        prompt = f"""
Generate an executive summary.

Lead

{lead}

Verification

{verification}

Classification

{classification}

Write a concise report.
"""
        report = self.llm.generate(prompt)

        state["report"] = report

        return state

    def generate_campaign_report(self) -> str:
        """
        Gathers statistics from the Google Sheet leads, generates a natural language
        executive report using Gemini, saves it to campaign_report.md, and emails the summary.
        """
        logger.info("Generating campaign-wide report...")
        try:
            leads = self.sheet.get_all_leads()
            if not leads:
                return "No leads found in the campaign database."

            total_leads = len(leads)
            verified_count = sum(1 for l in leads if str(l.get("Email Verified")).strip().upper() == "Y")
            emails_sent_count = sum(1 for l in leads if str(l.get("Email Sent")).strip().upper() == "Y")
            
            # Response statistics
            responses = [str(l.get("Response Status")).strip() for l in leads if l.get("Response Status")]
            response_counts = {}
            for r in responses:
                if r:
                    response_counts[r] = response_counts.get(r, 0) + 1
            
            # Sentiments
            sentiments = [str(l.get("Sentiment")).strip() for l in leads if l.get("Sentiment")]
            sentiment_counts = {}
            for s in sentiments:
                if s:
                    sentiment_counts[s] = sentiment_counts.get(s, 0) + 1

            # High priority leads
            priority_leads = []
            for l in leads:
                p_val = l.get("Lead Priority")
                try:
                    if p_val and int(str(p_val).strip()) >= 75:
                        priority_leads.append(l)
                except ValueError:
                    continue

            priority_summary = "\n".join([
                f"- {l.get('Lead Name')} ({l.get('Company')}) - Score: {l.get('Lead Priority')} - Response: {l.get('Response Status') or 'No response yet'}"
                for l in priority_leads
            ])

            stats_summary = f"""
Campaign Statistics:
- Total Leads: {total_leads}
- Verified Emails: {verified_count} ({(verified_count/total_leads)*100 if total_leads > 0 else 0:.1f}%)
- Outreach Emails Sent: {emails_sent_count}
- Responses Received: {len(responses)}
- Response Categories: {response_counts}
- Sentiments: {sentiment_counts}

High-Priority Leads (Score >= 75):
{priority_summary if priority_summary else 'None'}
"""
            prompt = f"""
You are the AI Supervisor Agent.
Review the following CRM campaign metrics and high-priority lead information, and generate a professional, insightful campaign summary report.
The report should include:
1. Executive summary of the campaign.
2. Metrics breakdown (in markdown table format).
3. Insights on response rate and sentiments.
4. Recommendations for next steps.

Metrics Data:
{stats_summary}

Write a clean, beautifully formatted markdown report.
"""
            report_content = self.llm.generate(prompt)
            if not report_content:
                report_content = f"Failed to generate campaign report content using LLM. Summary Stats:\n{stats_summary}"

            # Save report locally
            report_path = Path("campaign_report.md")
            report_path.write_text(report_content, encoding="utf-8")
            logger.info(f"Campaign report saved locally to {report_path.absolute()}")

            # Email the report to the supervisor
            subject = f"AI CRM Campaign Report - {datetime.date.today().strftime('%Y-%m-%d')}"
            email_sent = self.smtp.send_email(
                recipient=self.smtp.email,
                subject=subject,
                body=report_content
            )
            if email_sent:
                logger.info("Campaign report emailed successfully.")
            else:
                logger.warning("Failed to email campaign report.")

            return report_content

        except Exception as e:
            logger.error(f"Error generating campaign report: {e}", exc_info=True)
            return f"Error generating campaign report: {str(e)}"