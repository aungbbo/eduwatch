import logging
import os

import resend

logger = logging.getLogger(__name__)

DEMO_RECIPIENT = "aungag1998@gmail.com"
SENDER = "EduWatch <onboarding@resend.dev>"


def send_price_alert_email(
    item_name: str,
    target_price: float,
    current_price: float,
) -> bool:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        logger.warning("RESEND_API_KEY not set; skipping email notification")
        return False

    resend.api_key = api_key

    savings = max(target_price - current_price, 0.0)
    subject = f"Price drop alert: {item_name} is now ${current_price:.2f}"
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 560px; margin: 0 auto; padding: 24px; color: #0f172a;">
      <h1 style="margin: 0 0 8px; font-size: 22px; color: #1e3a8a;">EduWatch price alert</h1>
      <p style="margin: 0 0 20px; color: #475569;">Good news — an item on your watchlist hit your target price.</p>

      <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; background: #f8fafc;">
        <p style="margin: 0 0 4px; font-size: 13px; color: #64748b;">Item</p>
        <p style="margin: 0 0 14px; font-size: 18px; font-weight: 600;">{item_name}</p>

        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Your target</td>
            <td style="padding: 6px 0; text-align: right; font-weight: 600;">${target_price:.2f}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Current lowest price</td>
            <td style="padding: 6px 0; text-align: right; font-weight: 600; color: #047857;">${current_price:.2f}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">You save</td>
            <td style="padding: 6px 0; text-align: right; font-weight: 600; color: #047857;">${savings:.2f}</td>
          </tr>
        </table>
      </div>

      <p style="margin: 20px 0 0; color: #64748b; font-size: 13px;">— EduWatch demo notification</p>

      <hr style="margin: 28px 0 16px; border: none; border-top: 1px solid #e2e8f0;" />
      <p style="margin: 0; text-align: center; font-size: 20px; font-style: italic; color: #1e3a8a; font-weight: 600; letter-spacing: 0.3px;">Smarter shopping for students.</p>
    </div>
    """.strip()

    try:
        resend.Emails.send(
            {
                "from": SENDER,
                "to": [DEMO_RECIPIENT],
                "subject": subject,
                "html": html,
            }
        )
        return True
    except Exception as exc:
        logger.exception("Failed to send price alert email: %s", exc)
        return False
