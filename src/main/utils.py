import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def app_site_absolute_url(path: str) -> str:
    """
    Build an absolute URL for email links when no HttpRequest is available.

    Prefer PUBLIC_SITE_URL in env (e.g. https://cscita.bc.edu) so links stay correct
    when deploying; falls back to SITE_HOSTNAME + scheme from DEBUG.
    """
    if not path.startswith("/"):
        path = "/" + path
    public = getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/")
    if public:
        return f"{public}{path}"
    host = getattr(settings, "SITE_HOSTNAME", "127.0.0.1:8000").strip()
    for prefix in ("https://", "http://"):
        if host.lower().startswith(prefix):
            host = host[len(prefix) :]
            break
    scheme = "http" if getattr(settings, "DEBUG", True) else "https"
    return f"{scheme}://{host}{path}"


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
        from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
        context = {"message_lines": message_lines}
        html_content = render_to_string("notification_email.html", context)
        text_content = "\n\n".join(message_lines)

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Notification email sent to {recipients}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")
