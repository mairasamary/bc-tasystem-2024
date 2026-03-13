import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_notification_email(subject, recipients, message_lines):
    """
    Send an HTML notification email.

    Args:
        subject: Email subject line.
        recipients: A single email string or list of email strings.
        message_lines: List of strings, each rendered as a paragraph.
    """
    if not recipients:
        return

    if isinstance(recipients, str):
        recipients = [recipients]

    try:
        from_email = settings.EMAIL_HOST_USER
        context = {"message_lines": message_lines}
        html_content = render_to_string("notification_email.html", context)
        text_content = "\n\n".join(message_lines)

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Notification email sent to {recipients}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")
