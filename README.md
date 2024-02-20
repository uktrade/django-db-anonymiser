# django-db-anoynmiser
Django app to create configurable anonymised DB dumps.

## Getting started

- Add `database-sanitiser>=1.1.0`, `faker>=4.18.0`, `boto3>=1.26.17` to python requirements
- Add this github repository as a submodule to your django application
- Add `db_anonymiser` to `INSTALLED_APPS`
- Set the following django settings;
    - `DB_ANONYMISER_CONFIG_LOCATION` - the location of your anonymisation yaml file
    - `DB_ANONYMISER_AWS_ENDPOINT_URL` - optional, custom URL for AWS (e.g. if using minio)
    - `DB_ANONYMISER_AWS_ACCESS_KEY_ID` - AWS access key ID for the S3 bucket to upload dumps to
    - `DB_ANONYMISER_AWS_SECRET_ACCESS_KEW` - AWS secret key for the S3 bucket to upload dumps to
    - `DB_ANONYMISER_AWS_REGION` - AWS region for the S3 bucket to upload dumps to
    - `DB_ANONYMISER_AWS_STORAGE_BUCKET_NAME` - AWS bucket name for the S3 bucket to upload dumps to
