# from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string

from users.models import User


def send_mail_template(email, subject, html_template, params=None):
    params = params or {}
    msg_plain = render_to_string(html_template, params)
    msg_html = render_to_string(html_template, params)
    if settings.EMAIL_ENABLED:

        send_mail(
            subject,
            msg_plain,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=msg_html
        )
    else:
        print(msg_html.replace('\n', ''))


def send_templated_mail_with_attachments(email, subject, html_template, params=None, attachments=None, request=None):
    try:
        if (User.objects.filter(
                (Q(email_bounce=True) | Q(email_complaint=True)),
                email=email)
                .count() > 0):
            return None

        from django.conf import settings
        from django.template.loader import render_to_string

        params = params or {}

        msg_html = render_to_string(html_template, params, request=request)

        if settings.EMAIL_ENABLED:
            from django.core.mail import EmailMessage
            message = EmailMessage(
                subject,
                msg_html,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                None,
            )
            message.content_subtype = 'html'
            for item in attachments:
                message.attach_file(item)
            message.send()
        else:
            print(msg_html.replace('\n', ''))
    except Exception as e:
        print(e)
        return None
