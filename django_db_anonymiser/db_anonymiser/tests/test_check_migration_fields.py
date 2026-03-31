import pytest
from django.core.management import call_command


HELPERS_PATH = (
    "django_db_anonymiser.db_anonymiser.management.commands"
    "._check_migration_fields_helpers"
)
COMMAND_PATH = (
    "django_db_anonymiser.db_anonymiser.management.commands.check_migration_fields"
)


def test_check_migration_fields_no_diff_content(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value=None)
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    call_command("check_migration_fields")
    mock_writer.error.assert_not_called()
    mock_writer.warning.assert_not_called()


def test_check_migration_fields_no_fields_or_models(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="# no ops")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=[])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    call_command("check_migration_fields")
    mock_writer.error.assert_not_called()
    mock_writer.warning.assert_not_called()


def test_check_migration_fields_all_fields_in_config(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[("user", "email")])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.check_fields_in_config", return_value=[])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch("django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "config.yml")
    call_command("check_migration_fields")
    mock_writer.error.assert_not_called()


def test_check_migration_fields_missing_fields_warns(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[("user", "phone")])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.check_fields_in_config", return_value=["user.phone"])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch(
        "django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "/path/to/config.yml"
    )
    call_command("check_migration_fields")
    error_calls = [call[0][0] for call in mock_writer.error.call_args_list]
    assert any("user.phone" in call for call in error_calls)
    warning_calls = [call[0][0] for call in mock_writer.warning.call_args_list]
    assert any("/path/to/config.yml" in call for call in warning_calls)


def test_check_migration_fields_new_model_warns(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=["Customer"])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch("django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "config.yml")
    call_command("check_migration_fields")
    warning_calls = [call[0][0] for call in mock_writer.warning.call_args_list]
    assert any("Customer" in call for call in warning_calls)
    mock_writer.error.assert_not_called()


def test_check_migration_fields_new_model_and_missing_fields(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(
        f"{HELPERS_PATH}.extract_new_fields", return_value=[("report", "notes")]
    )
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=["Customer"])
    mocker.patch(
        f"{HELPERS_PATH}.check_fields_in_config", return_value=["report.notes"]
    )
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch("django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "config.yml")
    call_command("check_migration_fields")
    error_calls = [call[0][0] for call in mock_writer.error.call_args_list]
    assert any("report.notes" in call for call in error_calls)
    warning_calls = [call[0][0] for call in mock_writer.warning.call_args_list]
    assert any("Customer" in call for call in warning_calls)
