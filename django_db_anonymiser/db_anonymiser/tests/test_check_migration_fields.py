import pytest

from django.core.management import call_command


def test_check_migration_fields_no_fields(mocker, mock_writer):
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".extract_new_fields",
        return_value=[],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands.check_migration_fields"
        ".helpers.make_writers",
        return_value=mock_writer,
    )
    # Should not raise SystemExit
    call_command("check_migration_fields")


def test_check_migration_fields_all_fields_in_config(mocker, mock_writer):
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".extract_new_fields",
        return_value=[("user", "email")],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".check_fields_in_config",
        return_value=[],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands.check_migration_fields.helpers.make_writers",
        return_value=mock_writer,
    )
    mocker.patch("django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "config.yml")
    # Should not raise SystemExit
    call_command("check_migration_fields")


def test_check_migration_fields_missing_fields_yes_input(mocker, mock_writer):
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".extract_new_fields",
        return_value=[("user", "phone")],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".check_fields_in_config",
        return_value=["user.phone"],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands.check_migration_fields.helpers.make_writers",
        return_value=mock_writer,
    )
    mocker.patch(
        "django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION",
        "/path/to/config.yml",
    )
    mocker.patch("builtins.input", return_value="y")
    with pytest.raises(SystemExit) as exc_info:
        call_command("check_migration_fields")
    assert exc_info.value.code == 1
    expected_header = "\n⚠️  New field(s) not found in anonymiser config:"
    expected_field = "   - user.phone"
    expected_warning_header = "\nIf these fields contain sensitive data, add them to:"
    expected_config_path = "   /path/to/config.yml\n"
    expected_blocked = (
        "\n❌ Commit blocked. Please add sensitive " "fields to anonymiser config.\n"
    )
    assert expected_header in mock_writer.error.call_args_list[0][0][0]
    assert expected_field in mock_writer.error.call_args_list[1][0][0]
    assert expected_warning_header in mock_writer.warning.call_args_list[0][0][0]
    assert expected_config_path in mock_writer.warning.call_args_list[1][0][0]
    assert expected_blocked in mock_writer.error.call_args_list[2][0][0]


def test_check_migration_fields_missing_fields_no_input(mocker, mock_writer):
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".extract_new_fields",
        return_value=[("user", "phone")],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".check_fields_in_config",
        return_value=["user.phone"],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands.check_migration_fields.helpers.make_writers",
        return_value=mock_writer,
    )
    mocker.patch(
        "django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION",
        "/path/to/config.yml",
    )
    mocker.patch("builtins.input", return_value="n")
    # Should not raise SystemExit
    call_command("check_migration_fields")
    expected_success = "\n✓ Proceeding with commit.\n"
    assert expected_success in mock_writer.success.call_args_list[0][0][0]


def test_check_migration_fields_missing_fields_invalid_response(mocker, mock_writer):
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".extract_new_fields",
        return_value=[("user", "phone")],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".check_fields_in_config",
        return_value=["user.phone"],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands.check_migration_fields.helpers.make_writers",
        return_value=mock_writer,
    )
    mocker.patch(
        "django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION",
        "/path/to/config.yml",
    )
    mocker.patch("builtins.input", return_value="maybe")
    with pytest.raises(SystemExit) as exc_info:
        call_command("check_migration_fields")
    assert exc_info.value.code == 1
    expected_invalid = "\n❌ Invalid response. Commit blocked.\n"
    assert expected_invalid in mock_writer.error.call_args_list[2][0][0]


def test_check_migration_fields_multiple_missing_fields(mocker, mock_writer):
    """Should list all missing fields in error message."""
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".extract_new_fields",
        return_value=[("user", "phone"), ("report", "data")],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands._check_migration_fields_helpers"
        ".check_fields_in_config",
        return_value=["user.phone", "report.data"],
    )
    mocker.patch(
        "django_db_anonymiser.db_anonymiser.management.commands.check_migration_fields.helpers.make_writers",
        return_value=mock_writer,
    )
    mocker.patch("django.conf.settings.DB_ANONYMISER_CONFIG_LOCATION", "config.yml")
    mocker.patch("builtins.input", return_value="n")
    # Should not raise SystemExit when user says no
    call_command("check_migration_fields")
    error_calls = [call[0][0] for call in mock_writer.error.call_args_list]
    assert any("user.phone" in call for call in error_calls)
    assert any("report.data" in call for call in error_calls)
