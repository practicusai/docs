---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus GenAI
    language: python
    name: practicus_genai
---

```python
# Before you begin make sure the application deployment settings have a database configuration
app_deployment_key = "appdepl"
app_prefix = "apps"
app_name = "my-db-using-app"
```

```python
import os
import practicuscore as prt
```

```python
db_schema, db_conn_str = prt.apps.prepare_db(
    prefix=app_prefix,
    app_name=app_name,
    deployment_setting_key=app_deployment_key,
)

print("Created db schema:", db_schema)
# print("Db connection string:", db_conn_str)
print("*** Carefully save the connection string since it will not be displayed again. ***")
```

### (Recommended) Saving db conenction string to Vault

```python
assert db_conn_str, "db_conn_str not defined"

prt.vault.create_or_update_secret("MY_APP_CONN_STR", db_conn_str)
# prt.db. methods will always look for 'PRT_DB_CONN_STR' OS env variable.
# Remember to restart notebook kernel if any OS env variable changes
os.environ["PRT_DB_CONN_STR"] = db_conn_str
```

```python
# Reloading notebook? read from vault
db_conn_str, age = prt.vault.get_secret("MY_APP_CONN_STR")
os.environ["PRT_DB_CONN_STR"] = db_conn_str
```

```python
# Made a mistake? Only in a development environment, you can reset the db with the below.
# prt.apps.remove_db() will delete the schema dedicated to the app
confirm = input(f"ALL DATA WILL BE DELETED for '{app_prefix}/{app_name}'\nContinue? (y/n)")

if confirm == "y":
    prt.apps.remove_db(
        prefix=app_prefix,
        app_name=app_name,
        deployment_setting_key=app_deployment_key,
    )
```

```python
print("Scaffolding db folder")
prt.db.init()
```

```python
# open db/models.py and uncomment Hero class
prt.db.revision("initial tables")
```

Note: Always review `db/migrations/versions` files

```python
# Apply the changes to the database.
# This is for dev/test. For production, you can have the deployed application auto-migrate db.
prt.db.upgrade()
# offline = True only generates SQL
# prt.db.upgrade(offline=True)
```

## Upserting static data
To upsert (insert, if exists update) enum-line tables to the database, open `db/static_data.py` and uncomment import, list generation lines.


```python
result = prt.db.upsert_static_data()

print("Upsert operation sumamry:")
for table, rows in result.items():
    print("Upserted", rows, "rows for table model:", table)
```

## Deploying database usign app
Deploying an application will automatically upgrade the database

Note: if you are deploying on a separate database server, the database schema/roles must be ready either 
you can run prt.apps.prepare_db() or manually create the db schema. See bittim of this page to learn how.

```python
import practicuscore as prt

visible_name = "My DB using app"
description = "An app that uses a database.."
icon = "fa-database"

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,
    visible_name=visible_name,
    description=description,
    icon=icon,
    # Database related
    personal_secrets=["MY_APP_CONN_STR:PRT_DB_CONN_STR"],
)

print("Booting UI :", app_url)
print("Booting API:", api_url)
```

```python
# open db/models.py, add new columns, make other changes
prt.db.revision("added columns")
```

```python
prt.db.upgrade()
```

## Using database in run-time

```python
from db import Hero
from sqlmodel import Session, create_engine


def add_rows():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    engine = create_engine(os.environ["PRT_DB_CONN_STR"], echo=True)

    with Session(engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.commit()
```

```python
add_rows()
```

<!-- #region -->
### Manual DB Schema creation
- If you would like to prepare the database manually, please run the below.
- `schema_name` must be in the following format `prefix__app_name` where `-` an `/` is replace with a `_`
- Examples:
    - prefix=`apps` and app_name=`my-db-using-app` schema_name would be `apps__my_db_using_app`
    - prefix=`apps/finance` and app_name=`some-app` schema_name would be `apps_finance__some_app`

```sql
CREATE SCHEMA schema_name
CREATE ROLE schema_name LOGIN PASSWORD '__add_password_here__';
ALTER ROLE schema_name IN DATABASE db_name SET search_path TO schema_name;
GRANT ALL ON SCHEMA schema_name TO schema_name;
```

### Static data entry
- You can enter static data for enum-like database tables by using db/static_data.py

```python
# You can upsert (insert, or update if exists) static data to your tables on application start
# First import your table models
from .models import EnumLikeModel

def get_static_data():
    # Then add rows for 'enum like' tables with static primary keys
    static_data = [
        EnumLikeModel(key="primary_key_1", name="Some Name"),
        EnumLikeModel(key="primary_key_2", name="Some Other Name"),
        # EnumLikeModel2(...
    ]

    return static_data

# Finally, call prt.db.upsert_static_data() to upsert the data in design time
# This is automatically done in run-time during application start.
```

### Notes on column renames, default values

- prt.db.revision() might not detect column renames. Instead it will delete the old column, and create a new one. For renames, please review the generated code under `db/migrations/versions` and change as needed.
- prt.db.revision() might not detect default values of columns. To add default values, please review the generated code under `db/migrations/versions` and change as needed.
<!-- #endregion -->


---

**Previous**: [API Triggers For Airflow](../../workflows/api-triggers-for-airflow.md) | **Next**: [Prtchatbot > Prtchatbot](../prtchatbot/prtchatbot.md)
