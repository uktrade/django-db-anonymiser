from unittest.mock import Mock, mock_open

from db_anonymiser.management.commands._check_migration_fields_helpers import (
    check_fields_in_config,
    extract_new_fields,
    extract_new_models,
)


def test_get_diff_content_no_migrations(mocker):
    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value = Mock(stdout="", returncode=0)
    result = extract_new_fields("")
    assert result == []


def test_extract_new_fields_no_addfield_operations():
    result = extract_new_fields("# Migration with no AddField")
    assert result == []


def test_extract_new_fields_single_field():
    diff_content = """
+    operations = [
+        migrations.AddField(
+            model_name='user',
+            name='email',
+            field=models.EmailField(),
+        ),
+    ]
"""
    result = extract_new_fields(diff_content)
    assert result == [("user", "email")]


def test_extract_new_fields_multiple_fields():
    diff_content = """
+        migrations.AddField(
+            model_name='user',
+            name='email',
+            field=models.EmailField(),
+        ),
+        migrations.AddField(
+            model_name='report',
+            name='sensitive_pii',
+            field=models.CharField(max_length=255),
+        ),
"""
    result = extract_new_fields(diff_content)
    assert result == [("user", "email"), ("report", "sensitive_pii")]


def test_extract_new_models_no_create_model():
    result = extract_new_models("# Migration with no CreateModel")
    assert result == []


def test_extract_new_models_single_model():
    diff_content = """
+        migrations.CreateModel(
+            name='Customer',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
+                ('name', models.CharField(max_length=100)),
+            ],
+        ),
"""
    result = extract_new_models(diff_content)
    assert result == ["Customer"]


def test_extract_new_models_multiple_models():
    diff_content = """
+        migrations.CreateModel(
+            name='Employee',
+            fields=[],
+        ),
+        migrations.CreateModel(
+            name='Department',
+            fields=[],
+        ),
"""
    result = extract_new_models(diff_content)
    assert result == ["Employee", "Department"]


def test_extract_new_models_ignores_add_field():
    diff_content = """
+        migrations.CreateModel(
+            name='Vendor',
+            fields=[],
+        ),
+        migrations.AddField(
+            model_name='report',
+            name='vendor_notes',
+            field=models.TextField(blank=True),
+        ),
"""
    result = extract_new_models(diff_content)
    assert result == ["Vendor"]


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
    result = check_fields_in_config(
        [("user", "email"), ("report", "sensitive_pii")], "config.yml", mock_writer
    )
    assert result == []


def test_check_fields_in_config_missing_field(mocker):
    config_content = """
strategy:
  user:
    email: faker.email
"""
    mocker.patch("builtins.open", mock_open(read_data=config_content))
    mock_writer = Mock()
    result = check_fields_in_config(
        [("user", "email"), ("user", "phone")], "config.yml", mock_writer
    )
    assert result == ["user.phone"]


def test_check_fields_in_config_missing_model(mocker):
    config_content = """
strategy:
  user:
    email: faker.email
"""
    mocker.patch("builtins.open", mock_open(read_data=config_content))
    mock_writer = Mock()
    result = check_fields_in_config(
        [("report", "sensitive_pii")], "config.yml", mock_writer
    )
    assert result == ["report.sensitive_pii"]


def test_check_fields_in_config_file_not_found(mocker):
    mocker.patch("builtins.open", side_effect=FileNotFoundError("Config not found"))
    mock_writer = Mock()
    result = check_fields_in_config([("user", "email")], "config.yml", mock_writer)
    assert result == []
    mock_writer.warning.assert_called_once_with(
        "Warning: Could not read config file: Config not found"
    )


def test_check_fields_in_config_empty_strategy(mocker):
    mocker.patch("builtins.open", mock_open(read_data="strategy: {}"))
    mock_writer = Mock()
    result = check_fields_in_config([("user", "email")], "config.yml", mock_writer)
    assert result == ["user.email"]
