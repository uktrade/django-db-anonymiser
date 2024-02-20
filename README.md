# django-db-anoynmiser
Django app to create configurable anonymised DB dumps.

## Getting started

- Add `database-sanitiser>=1.1.0`, `faker>=4.18.0`, `boto3>=1.26.17` to python requirements
- Add this github repository as a submodule to your django application
- Add `db_anonymiser` to `INSTALLED_APPS`
- Set the following django settings;
    - `DB_ANONYMISER_CONFIG_LOCATION` - the location of your anonymisation yaml file
