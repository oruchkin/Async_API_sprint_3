# src/api/logging_config.py

import logging
from pythonjsonlogger import jsonlogger
from flask import request

# Настройка JSON логирования
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s')

json_handler = logging.FileHandler(filename='ugc_logs.json')
json_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        # Обеспечить, что request_id добавляется в лог при каждом запросе
        record.request_id = request.headers.get('X-Request-Id', 'unknown')
        return True


logger.addFilter(RequestIdFilter())
