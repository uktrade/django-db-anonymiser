from unittest.mock import Mock, mock_open

from db_anonymiser.management.commands._check_migration_fields_helpers import (
    check_fields_in_config,
    extract_new_fields,
)


def test_extract_new_fields_no_migrations(mocker):
    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value = Mock(stdout="", returncode=0)
    result = extract_new_fields()
    assert result == []


def test_extract_new_fields_no_addfield_operations(mocker):
    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.side_effect = [
        Mock(stdout="app/migrations/0001_initial.py", returncode=0),
        Mock(stdout="# Migration with no AddField", returncode=0),
    ]
    result = extract_new_fields()
    assert result == []


def test_extract_new_fields_single_field(mocker):
    mock_subprocess = mocker.patch("subprocess.run")
    diff_content = """
diff --git a/app/migrations/0001_initial.py b/app/migrations/0001_initial.py
+    operations = [
+        migrations.AddField(
+            model_name='user',
+            name='email',
+            field=models.EmailField(),
+        ),
+    ]
"""
    mock_subprocess.side_effect = [
        Mock(stdout="app/migrations/0001_initial.py", returncode=0),
        Mock(stdout=diff_content, returncode=0),
    ]
    result = extract_new_fields()
    assert result == [("user", "email")]


def test_extract_new_fields_multiple_fields(mocker):
    mock_subprocess = mocker.patch("subprocess.run")
    diff_content = """
+        migrations.AddField(
+            model_name='user',
+            name='email',
+        ),
+        migrations.AddField(
+            model_name='report',
+            name='sensitive_pii',
+        ),
"""
    mock_subprocess.side_effect = [
        Mock(stdout="app/migrations/0001_initial.py", returncode=0),
        Mock(stdout=diff_content, returncode=0),
    ]
    result = extract_new_fields()
    assert result == [("user", "email"), ("report", "sensitive_pii")]


def test_check_fields_in_config_all_present(mocker):
    config_content = """
strategy:
  user:
    email: faker.email
  report:
    sensitive_pii: faker.name
"""
    mocker.patch("builtins.open", mock_open(read_data=config_content))
    mock_writer = Mock()
    new_fields = [("user", "email"), ("report", "sensitive_pii")]
    result = check_fields_in_config(new_fields, "config.yml", mock_writer)
    assert result == []


def test_check_fields_in_config_missing_field(mocker):
    config_content = """
strategy:
  user:
    email: faker.email
"""
    mocker.patch("builtins.open", mock_open(read_data=config_content))
    mock_writer = Mock()
    new_fields = [("user", "email"), ("user", "phone")]
    result = check_fields_in_config(new_fields, "config.yml", mock_writer)
    assert result == ["user.phone"]


def test_check_fields_in_config_missing_model(mocker):
    config_content = """
strategy:
  user:
    email: faker.email
"""
    mocker.patch("builtins.open", mock_open(read_data=config_content))
    mock_writer = Mock()
    new_fields = [("report", "sensitive_pii")]
    result = check_fields_in_config(new_fields, "config.yml", mock_writer)
    assert result == ["report.sensitive_pii"]


def test_check_fields_in_config_file_not_found(mocker):
    mocker.patch("builtins.open", side_effect=FileNotFoundError("Config not found"))
    mock_writer = Mock()
    new_fields = [("user", "email")]
    result = check_fields_in_config(new_fields, "config.yml", mock_writer)
    assert result == []
    mock_writer.warning.assert_called_once_with(
        "Warning: Could not read config file: Config not found"
    )


def test_check_fields_in_config_empty_strategy(mocker):
    config_content = """
strategy: {}
"""
    mocker.patch("builtins.open", mock_open(read_data=config_content))
    mock_writer = Mock()
    new_fields = [("user", "email")]
    result = check_fields_in_config(new_fields, "config.yml", mock_writer)
    assert result == ["user.email"]
