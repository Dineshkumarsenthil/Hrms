import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template

from .models import EmailLog, EmailTemplate
from .templates_default import DEFAULT_TEMPLATES

log = logging.getLogger(__name__)


def get_template(code):
    """DB template wins (admin can edit); falls back to built-in default and stores it."""
    tpl = EmailTemplate.objects.filter(code=code).first()
    if tpl:
        return tpl.subject, tpl.body
    subject, body = DEFAULT_TEMPLATES[code]
    EmailTemplate.objects.create(code=code, subject=subject, body=body)
    return subject, body


def send_templated(code, to_email, context):
    """Render a template, send it, and ALWAYS write an EmailLog row. Never raises."""
    if not to_email:
        return None
    ctx = {"company": settings.COMPANY_NAME, **context}
    subject_t, body_t = get_template(code)
    subject = Template(subject_t).render(Context(ctx)).strip()
    body = Template(body_t).render(Context(ctx))
    status, error = EmailLog.Status.SENT, ""
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
    except Exception as exc:  # SMTP down etc. must not break the business action
        status, error = EmailLog.Status.FAILED, str(exc)
        log.warning("Email failed: %s", exc)
    # do not store plain-text passwords in the log
    logged_body = body.replace(str(context.get("password", "")), "********") if context.get("password") else body
    return EmailLog.objects.create(template_code=code, to_email=to_email, subject=subject, body=logged_body, status=status, error=error)
