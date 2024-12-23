from flask import render_template
from flask_mailman import EmailMultiAlternatives

from .version import __version_info_str__


def send_email(
    subject: str,
    email_file: str,
    from_addr: str,
    to_addr: list | tuple,
    extra_headers: dict,
    copy_admin: bool | str = False,
) -> dict:
    if not extra_headers:
        extra_headers = {}
    msg = EmailMultiAlternatives()
    msg.subject = subject.strip()
    txt_content = render_template(f"emails/{email_file}.txt")
    html_content = render_template(f"emails/{email_file}.html")
    msg.text_content = txt_content
    msg.attach_alternative(html_content, "text/html")
    msg.from_email = from_addr.strip()
    msg.to = to_addr
    extra_headers = extra_headers.update({"X-limelight": __version_info_str__})
    msg.headers = extra_headers
    if copy_admin:
        msg.bcc = [
            copy_admin,
        ]
    try:
        return {"result": msg.send(fail_silently=False)}
    except Exception as e:
        return e
