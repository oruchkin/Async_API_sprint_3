import logging
import smtplib
from email.message import EmailMessage

from src.core.settings import SMTPSettings


class SMTPMailSender:
    """
    Do not ever use that in production. NEVER!
    For internal testing purposes only.
    """

    def __init__(self, settings: SMTPSettings):
        self._settings = settings
        self._logger = logging.getLogger(__name__)

    def send(self, addr_to: list[str], subject: str, body: str) -> None:
        server = smtplib.SMTP_SSL(self._settings.host, self._settings.port)
        server.login(self._settings.login, self._settings.password)

        message = EmailMessage()
        addr_from = f"{self._settings.login}@ya.ru"
        message["From"] = addr_from
        message["To"] = ",".join(addr_to)
        message["Subject"] = subject
        message.add_alternative(body, subtype="html")
        try:
            server.sendmail(addr_from, addr_to, message.as_string())
        except smtplib.SMTPException as exc:
            reason = f"{type(exc).__name__}: {exc}"
            self._logger.error("Failed to send email %s to %s: %s", subject, ",".join(addr_to), reason)
        else:
            self._logger.info("Email %s was sent", subject)
        finally:
            server.close()
