import logging
import smtplib
from email.message import EmailMessage

from src.core.settings import MailhogSettings


class MailhogMailSender:
    def __init__(self, settings: MailhogSettings):
        self._settings = settings
        self._logger = logging.getLogger(__name__)

    @property
    def enabled(self) -> bool:
        return self._settings.enabled

    def send(self, to: str, subject: str, body: str) -> None:
        self._logger.info(f"Sending email to {to} with subject {subject} and body {body}")
        server = smtplib.SMTP(self._settings.host, self._settings.port)

        message = EmailMessage()
        addr_from = self._settings.sender
        message["From"] = addr_from
        message["To"] = to
        message["Subject"] = subject
        message.add_alternative(body, subtype="html")
        try:
            server.sendmail(addr_from, to, message.as_string())
        except smtplib.SMTPException as exc:
            reason = f"{type(exc).__name__}: {exc}"
            self._logger.error("Failed to send email %s to %s: %s", subject, to, reason)
        else:
            self._logger.info("Email %s was sent", subject)
        finally:
            server.close()
        self._logger.info("Email sent successfully")


def get_mailhog_mail_sender() -> MailhogMailSender:
    settings = MailhogSettings()
    return MailhogMailSender(settings)
