import functools
import os

from abc import ABC, abstractmethod

from django.core.management.base import BaseCommand

ETL_DATA_DIR = os.getenv("ETL_DATA_DIR", "prompt_payments/tests/data/")


class WriterBase(ABC):
    @abstractmethod
    def info(self, message: str):
        pass  # pragma: no cover

    @abstractmethod
    def success(self, message: str):
        pass  # pragma: no cover

    @abstractmethod
    def notice(self, message: str):
        pass  # pragma: no cover

    @abstractmethod
    def warning(self, message: str):
        pass  # pragma: no cover

    @abstractmethod
    def error(self, message: str):
        pass  # pragma: no cover


def make_writers(handler: BaseCommand):
    """Make writers.

    Given a BaseCommand instance, returns a dictionary of writer functions
    using the relevant styles.
    """

    class Writer:
        info = functools.partial(
            handler.stdout.write, style_func=handler.style.MIGRATE_HEADING
        )
        success = functools.partial(
            handler.stdout.write, style_func=handler.style.SUCCESS
        )
        notice = functools.partial(
            handler.stdout.write, style_func=handler.style.NOTICE
        )
        warning = functools.partial(
            handler.stdout.write, style_func=handler.style.WARNING
        )
        error = functools.partial(handler.stdout.write, style_func=handler.style.ERROR)

    return Writer()
