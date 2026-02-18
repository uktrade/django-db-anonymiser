import pytest

from django.core.management import call_command


HELPERS_PATH = (
    "django_db_anonymiser.db_anonymiser.management.commands"
    "._check_migration_fields_helpers"
)
COMMAND_PATH = (
    "django_db_anonymiser.db_anonymiser.management.commands" ".check_migration_fields"
)


def test_check_migration_fields_no_diff_content(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value=None)
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    call_command("check_migration_fields")
    mock_writer.error.assert_not_called()


def test_check_migration_fields_no_fields_or_models(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="# no ops")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=[])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    call_command("check_migration_fields")
    mock_writer.error.assert_not_called()


def test_check_migration_fields_all_fields_in_config(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[("user", "email")])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.check_fields_in_config", return_value=[])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch("django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "config.yml")
    call_command("check_migration_fields")
    mock_writer.error.assert_not_called()


def test_check_migration_fields_missing_fields_yes(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[("user", "phone")])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.check_fields_in_config", return_value=["user.phone"])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch(
        "django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "/path/to/config.yml"
    )
    mocker.patch("builtins.input", return_value="y")
    call_command("check_migration_fields")
    mock_writer.success.assert_called_once()


def test_check_migration_fields_missing_fields_no(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[("user", "phone")])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.check_fields_in_config", return_value=["user.phone"])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch(
        "django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "/path/to/config.yml"
    )
    mocker.patch("builtins.input", return_value="n")
    with pytest.raises(SystemExit) as exc_info:
        call_command("check_migration_fields")
    assert exc_info.value.code == 1


def test_check_migration_fields_missing_fields_invalid(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[("user", "phone")])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.check_fields_in_config", return_value=["user.phone"])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch(
        "django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "/path/to/config.yml"
    )
    mocker.patch("builtins.input", return_value="maybe")
    with pytest.raises(SystemExit) as exc_info:
        call_command("check_migration_fields")
    assert exc_info.value.code == 1
    assert (
        "\n❌ Invalid response. Commit blocked.\n"
        in mock_writer.error.call_args_list[-1][0][0]
    )


def test_check_migration_fields_new_model_prompts_user(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=["Customer"])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch("django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "config.yml")
    mocker.patch("builtins.input", return_value="y")
    call_command("check_migration_fields")
    warning_calls = [call[0][0] for call in mock_writer.warning.call_args_list]
    assert any("Customer" in call for call in warning_calls)
    mock_writer.success.assert_called_once()


def test_check_migration_fields_new_model_blocked(mocker, mock_writer):
    mocker.patch(f"{HELPERS_PATH}.get_diff_content", return_value="diff content")
    mocker.patch(f"{HELPERS_PATH}.extract_new_fields", return_value=[])
    mocker.patch(f"{HELPERS_PATH}.extract_new_models", return_value=["Customer"])
    mocker.patch(f"{COMMAND_PATH}.helpers.make_writers", return_value=mock_writer)
    mocker.patch("django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "config.yml")
    mocker.patch("builtins.input", return_value="n")
    with pytest.raises(SystemExit) as exc_info:
        call_command("check_migration_fields")
    assert exc_info.value.code == 1


def test_check_migration_fields_new_model_and_missing_fields(mocker, mock_writer):
    """Both CreateModel and missing AddField fields — single prompt covers both."""
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
    mocker.patch("builtins.input", return_value="y")
    call_command("check_migration_fields")
    # Only one prompt despite two issues
    assert mock_writer.success.call_count == 1
