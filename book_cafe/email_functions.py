import smtplib
from email.mime.text import MIMEText

from book_cafe.logging import logger
from confidential import EMAIL_PASSWORD, EMAIL_SENDER
from configuration import MAIL_SERVER_URL, MAIL_SERVER_PORT


def send_email(mail_subject: str, mail_text: str, recipients: list[str]):
    msg = MIMEText(mail_text)
    msg['Subject'] = mail_subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL(MAIL_SERVER_URL, MAIL_SERVER_PORT) as smtp_server:
        smtp_server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp_server.sendmail(EMAIL_SENDER, recipients, msg.as_string())
    logger.info(f"Email sent to {recipients}.")


if __name__ == "__main__":
    pass
