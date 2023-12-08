import ssl
import smtplib

from src.config import config
import src.celery_ as _celery


context = ssl.create_default_context()


@_celery.celery.task(soft_time_limit=8, expires=25)
def send_mail_message(
    recipient: str,
    message_as_string: str,
):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(config.MAIL_SENDER, config.MAIL_PASSWORD)
        server.sendmail(config.MAIL_SENDER, recipient, message_as_string)
