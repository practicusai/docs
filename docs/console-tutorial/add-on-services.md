# Add-On Services Documentation

## Overview
This document outlines how to manage and configure Add-On Services within the Practicus AI platform. It includes steps for adding new services, defining service types, and assigning connections for database, object storage, and Git repositories.

---

## Add Add-On Service

To add a new Add-On Service, follow these steps:

1. Navigate to **Add-On Services** > **Add Add-On Service**.


2. Fill in the required fields:
   - **Key**: Enter a unique key for the service.
   - **Name**: Provide a user-friendly name for the service.
   - **Add-On Service Type**: Select the type of service from the dropdown menu.
   - **URL**: Enter the primary URL of the service.

      ![](img\add_on_02.png)

3. Optional fields:
   - **Enterprise SSO App**: If applicable, select an SSO app to authenticate users with Practicus AI login credentials.
   - **Database Connection**: Choose a database connection if the service requires database access.
   - **Object Storage Connection**: Select an object storage connection for data storage.
   - **Git Repo Connection**: Specify a Git repository connection if the service integrates with a repository.

      ![](img\add_on_03.png)

4. Click **Save**, or choose **Save and add another** to configure additional services.

---

## Add Add-On Service Type

To define a new service type, follow these steps:

1. Navigate to **Add-On Services** > **Add-On Service Types** > **Add Add-On Service Type**.

2. Fill in the fields:
   - **Key**: Enter a unique identifier for the service type.
   - **Name**: Provide a descriptive name for the service type.

      ![](img\add_on_04.png)

3. Click **Save**, or choose **Save and add another** to configure additional service types.

---

[< Previous](object-storage.md) | [Next >](enterprise-sso.md)