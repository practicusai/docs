---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Automated relational database schema management

This example demonstrates how to use `prt.db` module to manage database schema migrations and static data, specifically for your Practicus AI applications.

**Core Concepts:**

1.  **Isolated Schemas:** Practicus AI encourages creating `separate restricted database schemas` (and corresponding users/roles) for each application to ensure `isolation and security`. This is handled by `prt.apps.prepare_db`.
2.  **Migrations:** Schema changes (creating tables, adding columns, etc.) are automatically managed by Practicus AI. This provides `version control` and `GitOps` capabilities for your database structure.
3.  **Models:** Database tables are defined using `SQLModel`, a popular python library that combines Pydantic and SQLAlchemy.
4.  **Workflow:**
    * Prepare the dedicated app schema (`prt.apps.prepare_db`).
    * Initialize the local migration environment (`prt.db.init`).
    * Define your data models (`db/models.py`).
    * Generate a migration script based on model changes (`prt.db.revision`).
    * Apply the migration to the database (`prt.db.upgrade`).
    * Optionally, define and load static/lookup data (`db/static_data.py`, `prt.db.upsert_static_data`).
    * Use the database in your application code.
    * Deploy the application, ensuring it has the database connection string.

**Prerequisites:**
* A system admin must configure a database connection for your Practicus AI `app deployment setting`, effectively making it `db-enabled`.
* Please see below `Preparing a Database for Your Applications` section to learn how.
* The `app_deployment_key` below refers to the key of this db-enabled app deployment setting.

## 1. Setup and Preparation

First, we define some parameters for our application.

```python
# Parameters
app_deployment_key = None  # must be db-enabled
app_prefix = "apps"
app_name = "my-db-app"
```

```python
# Sanity check
assert app_deployment_key, "app_deployment_key not defined"
assert app_prefix, "app_prefix not defined"
assert app_name, "app_name not defined"
```

If you don't know which app app deployment settings are `db-enabled`, you can list the app deployment settings you have acess to and check the `db_enabled` column running the below.

```python
import practicuscore as prt

my_app_settings = prt.apps.get_deployment_setting_list()

print("Application deployment settings I have access to:")
display(my_app_settings.to_pandas())
```

```python
# Let's verify our app deployment setting is db-enabled
verified = False
for app_setting in my_app_settings:
    if app_setting.key == app_deployment_key:
        if not app_setting.db_enabled:
            raise SystemError(f"Setting '{app_deployment_key}' is not db-enabled.")
        verified = True
        break

if not verified:
    raise ValueError(f"Setting '{app_deployment_key}' could not be located.")

print(f"Located setting '{app_deployment_key}' and it is db-enabled. Good to go!")
```

### 1.1. Prepare the Application Database Schema

We use `prt.apps.prepare_db` to create a dedicated schema and user/role for our application in the configured database. This function returns the schema name and a unique connection string.

**Important:** The connection string grants access only to the newly created schema. **Save it securely**, as it won't be shown again.

```python
print(f"Preparing database schema for app: {app_prefix}/{app_name} using deployment setting: {app_deployment_key}")
try:
    db_schema, db_conn_str = prt.apps.prepare_db(
        prefix=app_prefix,
        app_name=app_name,
        deployment_setting_key=app_deployment_key,
    )

    print(f"Successfully prepared database schema: {db_schema}")
    # print(f"Database connection string: {db_conn_str}") # Uncomment locally to see if needed, but avoid printing secrets.
    print("*** Connection string obtained. Please handle it securely. ***")
except Exception as e:
    print(f"Error preparing database: {e}")
    print("Please ensure the deployment setting key is correct and the database is accessible.")
    raise
```

### 1.2. Securely Store and Use the Connection String

It's highly recommended to store sensitive information like database connection strings in Practicus AI's Vault.

The `prt.db` commands (`revision`, `upgrade`, `upsert_static_data`) expect the connection string to be available in the environment variable `PRT_DB_CONN_STR`. We'll store it in Vault and then set the environment variable for the current notebook session.

```python
import os

# Define a unique name for the secret where we'll store the DB connection string.
db_conn_secret_name = f"{app_prefix.replace('/', '_')}__{app_name.replace('-', '_')}__CONN_STR".upper()
print(f"Database connection string will be stored in Vault secret: {db_conn_secret_name}")

# Store the connection string in Vault
print(f"Storing connection string in Vault secret: {db_conn_secret_name}")
prt.vault.create_or_update_secret(db_conn_secret_name, db_conn_str)

# Set the OS environment variable for prt.db commands in this session
# IMPORTANT: Restart the notebook kernel if you change this variable elsewhere!
os.environ["PRT_DB_CONN_STR"] = db_conn_str
print("Environment variable PRT_DB_CONN_STR set for this session.")
```

### 1.3. (Optional) Reload Connection String from Vault

If you restart the notebook kernel or run this notebook later, you can retrieve the connection string from Vault instead of running `prepare_db` again (which would try to recreate the schema).

```python
print(f"Attempting to reload connection string from Vault secret: {db_conn_secret_name}")
try:
    db_conn_str, age = prt.vault.get_secret(db_conn_secret_name)
    os.environ["PRT_DB_CONN_STR"] = db_conn_str
    print(f"Successfully reloaded connection string from Vault (Age: {age}).")
    print("Environment variable PRT_DB_CONN_STR set for this session.")
except Exception as e:
    print(f"Error reloading secret {db_conn_secret_name}: {e}")
    print("Ensure the secret exists and you have permissions.")
```

### 1.4. (Optional/Development Only) Remove Database Schema

If you need to start over **during development**, you can remove the application's database schema and associated user/role using `prt.apps.remove_db`. 

**⚠️ WARNING: This operation is destructive and will delete all data within the application's schema. Use with extreme caution, primarily in development environments.**

```python
# --- Development Only: Reset Database Schema ---
# Set this to True only if you understand the consequences and want to delete the schema
run_db_removal = False

if run_db_removal:
    print("*** WARNING: Proceeding with database schema removal! ***")
    confirm = input(f"Type 'delete {app_prefix}/{app_name}' to confirm DELETION of schema and data: ")

    if confirm == f"delete {app_prefix}/{app_name}":
        print(f"Removing database schema for app: {app_prefix}/{app_name}")
        try:
            prt.apps.remove_db(
                prefix=app_prefix,
                app_name=app_name,
                deployment_setting_key=app_deployment_key,
            )
            print("Database schema removed successfully.")
            # Unset the environment variable as the connection is now invalid
            if "PRT_DB_CONN_STR" in os.environ:
                del os.environ["PRT_DB_CONN_STR"]
                print("PRT_DB_CONN_STR environment variable unset.")
            # Clear the variable in the notebook context
            if "db_conn_str" in locals():
                del db_conn_str

        except Exception as e:
            print(f"Error removing database schema: {e}")
    else:
        print("Confirmation failed. Database schema not removed.")
else:
    print("Database removal step skipped (run_db_removal is False).")
```

## 2. Core `prt.db` Workflow

Now that we have a database schema and connection string ready, we can use the `prt.db` functions to manage the schema structure.


### 2.1. Initialize Migration Environment (`prt.db.init`)

This command scaffolds the necessary directory structure (`db/`, `db/migrations/`) and configuration files (`db/migrations.ini`, `db/migrations/env.py`, etc.) for Alembic in your current working directory.

It also creates template files:
* `db/models.py`: Where you'll define your database tables using `SQLModel`.
* `db/static_data.py`: Where you can define static lookup data.
* `db/__init__.py`: Makes the `db` directory a Python package.

Run this once per project. Use `overwrite=True` if you need to regenerate the configuration files (this won't overwrite your `models.py` or `static_data.py` unless they don't exist).

```python
print("Initializing database migration environment in the current directory...")
# Use overwrite=True cautiously if you have existing custom configurations
prt.db.init(overwrite=False)
print("Initialization complete. Check the 'db' folder.")
print("Next step: Edit db/models.py to define your database tables.")
```

<!-- #region -->
### 2.2. Define Data Models

Now, you need to **edit the `db/models.py` file**.

Define your database tables as classes inheriting from `SQLModel`. Here's an example based on the template created by `prt.db.init` (uncomment and modify the `Hero` class):

```python
# Example content for db/models.py
from typing import Optional
from sqlmodel import Field, SQLModel

# Define your table models here
# Example:
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)

# You can add more models/tables below
# class Item(SQLModel, table=True):
#     ...
```

**Action Required:** Open `db/models.py` in the file browser, uncomment or add your `SQLModel` classes, and save the file.
<!-- #endregion -->

### 2.3. Create a Database Revision (`prt.db.revision`)

After defining or modifying your models in `db/models.py`, run `prt.db.revision`. This command inspects your models and compares them to the database state recorded in previous migrations. It then automatically generates a new migration script in the `db/migrations/versions/` directory.

Provide a short, descriptive message (max 75 chars) for the revision.

**Important:** Always **review the generated Python script** in `db/migrations/versions/` before proceeding. Auto-detection isn't perfect, especially for complex changes like column renames or constraints. You may need to edit the script manually.

```python
# Make sure you have edited and saved db/models.py before running this!
revision_message = "Create initial tables"  # Change this message for subsequent revisions
print(f"Generating database revision with message: '{revision_message}'")

assert os.environ.get("PRT_DB_CONN_STR"), "PRT_DB_CONN_STR environment variable not set. Cannot run revision."

try:
    prt.db.revision(revision_message)
    print("Revision script generated in db/migrations/versions/")
    print("*** IMPORTANT: Please review the generated script before running upgrade. ***")
except Exception as e:
    print(f"Error generating revision: {e}")
    print("Check db/models.py for syntax errors and ensure the database is accessible.")
    # raise # Optional: Stop if revision fails
```

### 2.4. Apply Migrations to Database (`prt.db.upgrade`)

Once you have reviewed (and if necessary, edited) the migration script(s), use `prt.db.upgrade` to apply the changes to the actual database.

* **Online Mode (default):** `prt.db.upgrade()` connects to the database (using `PRT_DB_CONN_STR`) and executes the migration scripts to bring the schema to the latest version.
* **Offline Mode:** `prt.db.upgrade(offline=True)` does *not* connect to the database. Instead, it generates a single SQL script containing all the necessary commands to upgrade the schema. You can review this SQL and execute it manually against your database (useful for production environments or when direct access from the notebook is restricted).

```python
print("Applying migrations to the database (Online Mode)...")

assert os.environ.get("PRT_DB_CONN_STR"), "PRT_DB_CONN_STR environment variable not set. Cannot run upgrade."

# --- Online Upgrade (Applies changes directly) ---
try:
    prt.db.upgrade()
    print("Database upgrade complete.")
except Exception as e:
    print(f"Error during online upgrade: {e}")
    # raise # Optional: Stop if upgrade fails

# --- Offline Upgrade (Generates SQL script) ---
# print("Generating SQL script for offline upgrade...")
# try:
#     prt.db.upgrade(offline=True)
#     print("SQL script generated. Check the console output.")
#     print("Review the SQL script and apply it manually to your database.")
# except Exception as e:
#     print(f"Error during offline upgrade generation: {e}")
```

<!-- #region -->
## 3. Managing Static Data (`prt.db.upsert_static_data`)

Some applications require lookup tables with predefined data (e.g., status types, categories). You can manage this using `db/static_data.py` and `prt.db.upsert_static_data`.

### 3.1. Define Static Data

**Edit the `db/static_data.py` file.** It should contain a function `get_static_data()` that returns a list of `SQLModel` instances representing the rows you want to insert or update.

**Important:** For the upsert logic to work correctly (updating existing rows instead of always inserting new ones), your static data models **must have static primary keys** defined in the data itself, not auto-incrementing keys.

```python
# Example content for db/static_data.py

# Import your models that hold static data
from .models import EnumLikeModel

def get_static_data():
    """Returns a list of SQLModel instances for static data."""
    static_data = [
        # Example using EnumLikeModel (replace with your actual models and data)
        EnumLikeModel(key="pending", name="Pending"),
        EnumLikeModel(key="in_progress", name="In Progress"),
        EnumLikeModel(key="completed", name="Completed", description="Task is finished"),
        # SomeOtherModel(... 
    ]
    return static_data
```

**Action Required:**
1. Ensure the models for your static data (e.g., `EnumLikeModel`) are defined in `db/models.py`.
2. Ensure these models have primary keys that you can set manually (not auto-incrementing).
3. Edit `db/static_data.py`, import your models, and populate the list returned by `get_static_data()`.
4. Make sure you have run `prt.db.revision` and `prt.db.upgrade` to create the necessary tables (`EnumLikeModel` in this example) *before* trying to upsert data.
<!-- #endregion -->

### 3.2. Upsert Static Data to Database

Run `prt.db.upsert_static_data()` to load the data defined in `db/static_data.py` into the database. It connects using `PRT_DB_CONN_STR` and performs an insert-or-update operation based on the primary key.

```python
# Make sure you have edited db/static_data.py and the corresponding tables exist in the DB.
print("Upserting static data from db/static_data.py...")

assert os.environ.get("PRT_DB_CONN_STR"), "PRT_DB_CONN_STR environment variable not set. Cannot upsert static data."

try:
    upsert_summary = prt.db.upsert_static_data()
    print("Upsert operation summary:")
    if upsert_summary:
        for model_name, count in upsert_summary.items():
            print(f"- Upserted {count} rows for model: {model_name}")
    else:
        print("- No static data found or processed. Check db/static_data.py.")
except ModuleNotFoundError:
    print(
        "ERROR: Could not import models or static data. Ensure 'db/models.py' and 'db/static_data.py' exist and are correct."
    )
except Exception as e:
    print(f"Error upserting static data: {e}")
    print("Ensure the tables exist (run upgrade) and have static primary keys.")
    # raise # Optional: Stop if upsert fails
```

## 4. Schema Evolution (Iteration)

As your application requirements change, you'll need to update your database schema:

1.  **Modify `db/models.py`:** Add new models (tables), add/remove/modify fields (columns) in existing models.
2.  **Run `prt.db.revision("Your descriptive message")`:** Generate a new migration script reflecting the changes.
3.  **Review the script** in `db/migrations/versions/`.
4.  **Run `prt.db.upgrade()`:** Apply the new migration to the database.

You can repeat this cycle as many times as needed.

```python
# Example: Suppose you added a 'last_updated' column to the Hero model in db/models.py

print("--- Simulating Schema Evolution ---")
print("1. Models modified (manually edit db/models.py)")

print("2. Generating new revision...")
try:
    prt.db.revision("Add last_updated to Hero")
    print("Review the new script in db/migrations/versions/")
except Exception as e:
    print(f"Error: {e}")

print("3. Applying upgrade...")
try:
    prt.db.upgrade()
    print("Upgrade applied.")
except Exception as e:
    print(f"Error: {e}")
```

## 5. Using the Database at Runtime

Once your schema is set up, you can interact with the database using standard `SQLModel` (or SQLAlchemy) patterns in your application code or notebooks. You'll need the connection string, which is typically retrieved from the `PRT_DB_CONN_STR` environment variable (set directly or via Vault secrets during deployment).

```python
from sqlmodel import Session, create_engine

# Ensure models are importable (because we ran init)
# If you get ModuleNotFoundError, restart kernel after running prt.db.init
try:
    from db.models import Hero
except ModuleNotFoundError:
    print("Could not import from db.models. Did you run prt.db.init and define models?")
    print("You might need to restart the notebook kernel.")
    raise


def add_hero_data():
    # Retrieve connection string from environment
    conn_str = os.environ.get("PRT_DB_CONN_STR")
    if not conn_str:
        print("Error: PRT_DB_CONN_STR not set. Cannot connect to database.")
        return

    print("Connecting to database using PRT_DB_CONN_STR OS env variable...")
    # Set echo=True to see SQL statements
    engine = create_engine(conn_str, echo=False)

    # Create sample data
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    print("Adding sample Hero data...")
    try:
        with Session(engine) as session:
            session.add(hero_1)
            session.add(hero_2)
            session.add(hero_3)
            session.commit()
            print("Data committed successfully.")

            # Example of retrieving data
            session.refresh(hero_1)
            print("Refreshed hero_1:", hero_1)

    except Exception as e:
        print(f"Database error during runtime usage: {e}")
        print("Ensure the table exists and the connection string is valid.")


add_hero_data()
```

## 6. Integration with Application Deployment

When deploying your application using `prt.apps.deploy`, you need to provide the database connection string to the running application container. This is typically done by:

1.  Storing the connection string as a secret in Vault (as done in step 1.2).
2.  Mapping this Vault secret to the `PRT_DB_CONN_STR` environment variable within the application container using the `personal_secrets` argument in `prt.apps.deploy`.

### Automatic Database Migration on App Deployment

By default, Practicus AI `automatically applies database migrations` (effectively running `prt.db.upgrade` and `prt.db.upsert_static_data`) whenever your application starts or restarts in a deployed environment, including production settings. This convenient feature helps ensure your database schema is synchronized with your application code. If you need to disable this behavior, for example, to manage migrations manually or through a separate CI/CD pipeline, simply set the environment variable `PRT_DB_SKIP_MIGRATION` to true in your application's deployment configuration.

```python
visible_name = "My Database App"
description = "An example app using prt.db for schema management."
icon = "fa-database"

print(f"Deploying app: {app_prefix}/{app_name}")
print(f"Mapping Vault secret '{db_conn_secret_name}' to env var 'PRT_DB_CONN_STR'")

try:
    app_url, api_url = prt.apps.deploy(
        deployment_setting_key=app_deployment_key,
        prefix=app_prefix,
        app_name=app_name,
        visible_name=visible_name,
        description=description,
        icon=icon,
        # --- Database Connection Mapping ---
        # Format: "VAULT_SECRET_NAME:TARGET_ENV_VAR_NAME"
        personal_secrets=[f"{db_conn_secret_name}:PRT_DB_CONN_STR"],
        # To disable automated db migration:
        # env_variables={"PRT_DB_SKIP_MIGRATION": "true"}
    )

    print("Deployment submitted.")
    print(f"App UI URL (once ready): {app_url}")
    print(f"App API URL (once ready): {api_url}")

except Exception as e:
    print(f"Error during deployment submission: {e}")
```

<!-- #region -->
## 7. A Guide for Admins: Preparing a Database for Your Applications 

Use the following SQL scripts as a guide to create the necessary database structure for your applications.

### 1. Create an Administrative Database Role (User)

First, create a dedicated administrative role. This role is primarily intended for control plane operations (e.g., automated setup scripts or administrative tools) to manage database artifacts for your applications.

* **Purpose:** This admin role (`prt_apps_admin` in the example) will be used to create more restricted, application-specific database roles and schemas. It is *not* intended for direct use by the applications themselves.
* **`CREATEROLE` Permission:** This permission is required because the admin role needs the ability to create separate, isolated database roles for each application, enhancing security and separation.
* **`LOGIN` Permission:** Allows this role to connect to the database server.

```sql
-- Create the administrative role
CREATE ROLE prt_apps_admin WITH
  LOGIN
  CREATEROLE
  PASSWORD '_your_password_'; -- Replace with a strong, secure password
```

### 2. Create a Dedicated Database (Recommended)

It's best practice to create a separate database specifically for your applications. Hosting this database on a dedicated server instance is also recommended for performance and isolation, if feasible.

* **`OWNER prt_apps_admin`**: Assigning the administrative role as the owner grants it initial full permissions within this new database, simplifying subsequent setup.

```sql
-- Create the application database and set the owner
CREATE DATABASE prt_apps
  OWNER prt_apps_admin;
```

### 3. Grant Necessary Permissions to the Admin Role

Ensure the administrative role has the essential permissions on the newly created database.

* **`CONNECT` Permission:** Allows the `prt_apps_admin` role to connect specifically to the `prt_apps` database.
* **`CREATE` Permission:** Allows the `prt_apps_admin` role to create new schemas within the `prt_apps` database. This is necessary for creating isolated schemas for different applications or services.

```sql
-- Grant connection access to the database
GRANT CONNECT ON DATABASE prt_apps TO prt_apps_admin;

-- Grant permission to create schemas within the database
GRANT CREATE ON DATABASE prt_apps TO prt_apps_admin;
```

### 4. Configure Application Deployment Settings

After setting up the administrative database role and database, you need to configure your `app deployment setting` to use them.

#### a. Construct the Connection String

You will need a standard PostgreSQL connection string to connect Practicus AI to the database you created.

* **Standard Format:** `postgresql://user:password@host/database`
* **Example (using the admin role):** `postgresql://prt_apps_admin:your_secure_password@your_database_host/prt_apps`
* **Using Practicus AI Password Management (Recommended):** To avoid hardcoding the password directly in the connection string, Practicus AI allows you to use a placeholder (`__PASSWORD__`) and store the password securely and separately within the platform.
    * **Format:** `postgresql://user:__PASSWORD__@host/database`
    * **Example:** `postgresql://prt_apps_admin:__PASSWORD__@prt-db-pg-1-rw.prt-ns.svc.cluster.local/prt_apps`
        *(Replace the host `prt-db-pg-1-rw.prt-ns.svc.cluster.local` with your actual database host address)*

#### b. Create a System Database Connection in Practicus AI

Next, register this connection within the Practicus AI Admin Console.

1.  Navigate to **Data Catalog** > **System DB Connections**.
2.  Click to add a new database connection (e.g., name it `my-db-for-apps`).
3.  Enter the connection string constructed in the previous step.
4.  **Recommendation:** Use the connection string format with `__PASSWORD__` and enter the actual password in the dedicated password field provided by Practicus AI. Save the connection.

#### c. Update Application Deployment Settings

Finally, link this database connection to your app deployment settings. This tells Practicus AI which database connection to use when apps need to create their own isolated database resources.

1.  Navigate to **App Hosting** > **Deployment Settings**.
2.  Either add a new deployment setting or edit an existing one.
3.  Scroll down to the **Database Connection** section.
4.  Select the System DB Connection you created earlier (e.g., `my-db-for-apps`) from the dropdown list.
5.  Save the deployment settings.

With this configuration complete, users creating new applications or updating existing ones through Practicus AI will now have the capability to automatically provision isolated database schemas and roles using the administrative database connection you've set up.

<!-- #endregion -->

## 8. Advanced Notes and Troubleshooting

### Migration Script Review
* **Column Renames:** Alembic's auto-generation often detects a column rename as a `drop_column` followed by an `add_column`, which causes data loss. Review the generated scripts in `db/migrations/versions/` and manually change these to use `op.alter_column(..., new_column_name='...')` if you need to preserve data during a rename.
* **Default Values & Constraints:** Auto-generation might miss default values, specific constraints, or index types. Check the generated scripts and add or modify Alembic operations (`op.`) as needed.
* **SQLModel vs. Alembic Types:** Ensure the data types in your `SQLModel` definitions translate correctly to Alembic/SQLAlchemy types in the migration scripts.

### Static Data Notes
* As emphasized before, use static primary keys in `db/static_data.py` for reliable upserts.
* `prt.db.upsert_static_data()` runs within a transaction. If any part fails, the entire operation for that run is rolled back.

### Environment Variables
* Changes to environment variables like `PRT_DB_CONN_STR` within a notebook session might not be picked up by subprocesses (like Alembic calls within `prt.db`) unless the kernel is restarted.

### File Locations
* `prt.db.init`, `revision`, `upgrade`, `upsert_static_data` all expect the `db` directory (containing `models.py`, `static_data.py`, `migrations.ini`, `migrations/`) to be in the **current working directory** where the Python command/notebook cell is executed.


---

**Previous**: [Sample Vector Db](../vector-databases/sample-vector-db.md) | **Next**: [Message Queues > Build](../message-queues/build.md)
