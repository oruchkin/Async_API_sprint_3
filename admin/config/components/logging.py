LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "debug-console": {"class": "logging.StreamHandler", "filters": ["require_debug_true"]},
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {"django.db.backends": {"level": "DEBUG", "handlers": ["debug-console"], "propagate": False}},
}
