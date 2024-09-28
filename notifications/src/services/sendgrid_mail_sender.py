import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from src.core.settings import SendgridSettings


class SendgridMailSender:
    def __init__(self, settings: SendgridSettings):
        self._settings = settings
        self._client = SendGridAPIClient(settings.api_key)
        self._logger = logging.getLogger(__name__)

    def send(self, to: str, subject: str, body: str) -> None:
        message = Mail(
            from_email=self._settings.sender,
            to_emails=to,
            subject=subject,
            html_content=body,
        )
        try:

            response = self._client.send(message)
            self._logger.info(response.status_code)
            self._logger.info(response.body)
            self._logger.info(response.headers)
        except Exception as e:
            # TODO: Send to the dead queue and so on
            self._logger.error(e)


def get_sendgrid_mail_sender() -> SendgridMailSender:
    settings = SendgridSettings()
    return SendgridMailSender(settings)
