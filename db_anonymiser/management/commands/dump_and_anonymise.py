import os
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from database_sanitizer.config import Configuration
from database_sanitizer.dump import run


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-local-dumpfile",
            action="store_true",
            help="Keep local dump file, rather than cleaning it up.",
        )

    def configure(self):
        self.keep_local_dumpfile = False
        self.temporary_dump_location = getattr(settings, "DB_ANONYMISER_TEMPORARY_DUMP_LOCATION", "/tmp/anonymised.sql")
        try:
            self.config_location = settings.DB_ANONYMISER_CONFIG_LOCATION
        except AttributeError:
            raise CommandError("DB_ANONYMISER_CONFIG_LOCATION must be set in django settings.")

    def handle(self, *args, **options):
        logger.info("Starting DB dump and anonymiser")
        self.configure()
            
        if options["keep_local_dumpfile"]:
            self.keep_local_dumpfile = True

        try:
            self.dump_anonymised_db()
            self.write_to_s3()
            logger.info("DB dump and anonymiser was successful!")
        finally:
            self.cleanup()

    def dump_anonymised_db(self):
        db_details = settings.DATABASES["default"]
        postgres_url = f"postgresql://{db_details['USER']}:{db_details['PASSWORD']}@{db_details['HOST']}:{db_details['PORT']}/{db_details['NAME']}"
        with open(self.temporary_dump_location, "w") as outfile:
            run(
                url=postgres_url,
                config=Configuration.from_file(self.config_location),
                output=outfile,
            )

    def write_to_s3(self):
        # write file to S3 location
        pass

    def cleanup(self):
        if self.keep_local_dumpfile:
            return
        try:
            os.remove(self.temporary_dump_location)
        except os.exceptions.FileNotFoundError:
            pass
