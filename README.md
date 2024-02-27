# django-db-anonymiser
Django app to create configurable anonymised DB dumps.

django-db-anonymiser provides a django app with a management command `dump_and_anonymise`.
This command runs a `pg_dump` against a postgresql DB, applies anonymisation functions to 
data dumped from the DB and then writes the anonymised dump to S3.
See here for lite-api's example anonymisation configuration; https://github.com/uktrade/lite-api/blob/dev/api/conf/anonymise_model_config.yaml

This pattern is designed as a replacement for Lite's old DB anonymisation process (although it is general purpose and can be used for any django project which uses postgresql).
The previous process was baked in to an airflow installation and involved making
a `pg_dump` from production, anonymising that dump with python and pushing the 
file to S3. See; https://github.com/uktrade/lite-airflow-dags/blob/master/dags/export_lite_db.py

django-db-anonymiser follows the same overall pattern, but aims to achieve it
through a django management command instead of running on top of airflow.  In addition,
the configuration for how DB columns are anonymised can be configured in simple YAML.

## Getting started

- Add `database-sanitizer>=1.1.0`, `faker>=4.18.0`, `boto3>=1.26.17` to python requirements; it is assumed python/psycopg and co are already installed.
- Add this github repository as a submodule to your django application
- Add `db_anonymiser` to `INSTALLED_APPS`
- Set the following django settings;
    - `DB_ANONYMISER_CONFIG_LOCATION` - the location of your anonymisation yaml file
    - `DB_ANONYMISER_AWS_ENDPOINT_URL` - optional, custom URL for AWS (e.g. if using minio)
    - `DB_ANONYMISER_AWS_ACCESS_KEY_ID` - AWS access key ID for the S3 bucket to upload dumps to
    - `DB_ANONYMISER_AWS_SECRET_ACCESS_KEW` - AWS secret key for the S3 bucket to upload dumps to
    - `DB_ANONYMISER_AWS_REGION` - AWS region for the S3 bucket to upload dumps to
    - `DB_ANONYMISER_AWS_STORAGE_BUCKET_NAME` - AWS bucket name for the S3 bucket to upload dumps to
