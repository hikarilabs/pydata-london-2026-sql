import sys
import structlog


def configure_logging() -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO+
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
    )


configure_logging()

logger = structlog.get_logger()
