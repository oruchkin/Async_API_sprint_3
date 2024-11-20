from typing import Callable

from prometheus_client import Counter
from prometheus_fastapi_instrumentator.metrics import Info


def http_requested_languages_total() -> Callable[[Info], None]:
    """
    Counts the number of times a certain language has been requested.
    """
    METRIC = Counter(
        "http_requested_languages_total",
        "Number of times a certain language has been requested.",
        labelnames=("langs",),
    )

    def instrumentation(info: Info) -> None:
        langs = set()
        lang_str = info.request.headers["Accept-Language"]
        for element in lang_str.split(","):
            element = element.split(";")[0].strip().lower()
            langs.add(element)
        for language in langs:
            METRIC.labels(language).inc()

    return instrumentation


movies_watch_amount = Counter(
    "movies_watch_amount",
    "Number of times a certain movie type has been watched.",
    labelnames=("type",),
)
