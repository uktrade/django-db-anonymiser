import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from . import _base_helpers as helpers
from . import _check_migration_fields_helpers as check_migration_fields_helpers


# class Command(BaseCommand):
#     help = "Check that new migration fields are in anonymiser config"

#     def handle(self, *args, **options):
#         writer = helpers.make_writers(self)
#         new_fields = check_migration_fields_helpers.extract_new_fields()
#         if not new_fields:
#             return
#         config_path = settings.DB_ANONYMISER_CONFIG_LOCATION
#         missing_fields = check_migration_fields_helpers.check_fields_in_config(
#             new_fields, config_path, writer
#         )
#         if missing_fields:
#             writer.error("\n⚠️  New field(s) not found in anonymiser config:")
#             for field in missing_fields:
#                 writer.error(f"   - {field}")
#             writer.warning("\nIf these fields contain sensitive data, add them to:")
#             writer.warning(f"   {config_path}\n")
#             response = (
#                 input("Do these fields contain sensitive data? (y/n): ").strip().lower()
#             )
#             if response == "y":
#                 writer.error(
#                     "\n❌ Commit blocked. "
#                     "Please add sensitive fields to anonymiser config.\n"
#                 )
#                 sys.exit(1)
#             elif response == "n":
#                 writer.success("\n✓ Proceeding with commit.\n")
#                 return
#             else:
#                 writer.error("\n❌ Invalid response. Commit blocked.\n")
#                 sys.exit(1)
#             sys.exit(1)


class Command(BaseCommand):
    help = "Check that new migration fields are in anonymiser config"

    def handle(self, *args, **options):
        writer = helpers.make_writers(self)
        config_path = settings.DB_ANONYMISER_CONFIG_LOCATION
        diff_content = check_migration_fields_helpers.get_diff_content()
        if not diff_content:
            return
        new_fields = check_migration_fields_helpers.extract_new_fields(diff_content)
        new_models = check_migration_fields_helpers.extract_new_models(diff_content)
        if not new_fields and not new_models:
            return
        # Handle AddField — check against config
        missing_fields = []
        if new_fields:
            missing_fields = check_migration_fields_helpers.check_fields_in_config(
                new_fields, config_path, writer
            )
            if missing_fields:
                writer.error("\n⚠️  New field(s) not found in anonymiser config:")
                for field in missing_fields:
                    writer.error(f"   - {field}")
                writer.warning("\nIf these fields contain sensitive data, add them to:")
                writer.warning(f"   {config_path}\n")
        # Handle CreateModel — always prompt
        if new_models:
            model_list = ", ".join(new_models)
            writer.warning(f"\n⚠️  New model(s) detected: {model_list}")
            writer.warning(
                "Please ensure any sensitive fields are added to the anonymiser config."
            )
        if missing_fields or new_models:
            response = input("Are you happy to proceed? (y/n): ").strip().lower()
            if response == "y":
                writer.success("\n✓ Proceeding with commit.\n")
                return
            elif response == "n":
                writer.error("\n❌ Commit blocked.\n")
                sys.exit(1)
            else:
                writer.error("\n❌ Invalid response. Commit blocked.\n")
                sys.exit(1)
