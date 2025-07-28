# Automating Kerberos Ticket Renewal with Cron

## Introduction

Kerberos tickets are essential for authenticating to various services, but they have a limited lifespan. When a ticket expires, you lose access to those services until you re-authenticate. Manually renewing tickets is a hassle, especially for automated processes. This notebook will guide you through creating a startup script that leverages the `cron` utility to automatically renew your Kerberos tickets at regular intervals, ensuring uninterrupted access to Kerberos-authenticated services.

## Why Automate Renewal with Cron?

`cron` is a powerful, time-based job scheduler in Unix-like operating systems. It lets you schedule commands or scripts to run automatically at specific times or intervals. Automating Kerberos ticket renewal with `cron` offers several key advantages:

* Uninterrupted Access: Ensures continuous access to Kerberos-authenticated services without manual intervention.
* Increased Reliability: Reduces the risk of authentication failures caused by expired tickets in automated workflows.
* Operational Efficiency: Frees up your time from the repetitive task of manual ticket renewal.

## Prerequisites

Before we start, make sure you have the following:

* Kerberos Principal (e.g., `your_user{{USER_NAME}}@{{REALM_NAME}}`).
* In this notebook, we'll automatically create a keytab file. While typically provided by a Kerberos administrator, our startup script handles this for convenience in certain scenarios.

## How the Script Was Encoded

The shell script content was converted into the long `base64` string you'll use by piping the script's raw text content to the `base64` command. Here's a breakdown of the process:

**The Original Script Content**

This is the multi-line shell script designed to create your keytab, get an initial Kerberos ticket, and set up the `cron` job. Each line performs a specific action:


```bash
{
  echo addent -password -p {{USER_NAME}}@{{REALM_NAME}} -k 1 -e aes256-cts
  echo {{PASSWORD}}
  echo wkt /var/practicus/{{USER_NAME}}.keytab
  echo q
} | ktutil
chmod 700 /var/practicus/{{USER_NAME}}.keytab
kinit -V -kt /var/practicus/{{USER_NAME}}.keytab {{USER_NAME}}@{{REALM_NAME}} -l 12h
service cron start
(crontab -l 2>/dev/null; echo '0 */11 * * * kinit -kt /var/practicus/{{USER_NAME}}.keytab {{USER_NAME}}@{{REALM_NAME}} -l 12h') | crontab -
sh /var/practicus/.practicus/entry.sh
```

* `{`: This starts a command group for `ktutil`.
* `echo addent -password -p {{USER_NAME}}@{{REALM_NAME}} -k 1 -e aes256-cts`: Adds a principal entry to the keytab using a password.
* `echo {{PASSWORD}}`: Provides the password for the principal.
* `echo wkt /var/practicus/{{USER_NAME}}.keytab`: Specifies the output keytab file path.
* `echo q`: Quits `ktutil`.
* `} | ktutil`: Pipes all the preceding `echo` commands into `ktutil` to create the keytab.
* `chmod 700 /var/practicus/{{USER_NAME}}.keytab`: Sets secure permissions for the keytab (owner only: read, write, execute).
* `kinit -V -kt /var/practicus/{{USER_NAME}}.keytab {{USER_NAME}}@{{REALM_NAME}} -l 12h`: Obtains an initial Kerberos TGT (Ticket Granting Ticket) using the keytab, valid for 12 hours.
* `service cron start`: Ensures the `cron` service is running.
* `(crontab -l 2>/dev/null; echo '0 */11 * * * kinit -kt /var/practicus/{{USER_NAME}}.keytab {{USER_NAME}}@{{REALM_NAME}} -l 12h') | crontab -`: Adds a cron job to renew the ticket every 11 hours. Note that `{{USER_NAME}}@{{REALM_NAME}}` appears to be a specific service principal that will have its ticket renewed.
* `sh /var/practicus/.practicus/entry.sh`: Executes another script. Its exact function depends on the content of that specific script, which is not defined here.

**Encoding with `echo` and `base64`:**

To convert this multi-line script into a single `base64` string, it's enclosed in quotes and then passed as input to the `base64` command using a pipe (`|`). The command used for encoding looks like this:

```bash
{
  echo addent -password -p {{USER_NAME}}@{{REALM_NAME}} -k 1 -e aes256-cts
  echo {{PASSWORD}}
  echo wkt /var/practicus/{{USER_NAME}}.keytab
  echo q
} | ktutil
chmod 700 /var/practicus/{{USER_NAME}}.keytab
kinit -V -kt /var/practicus/{{USER_NAME}}.keytab {{USER_NAME}}@{{REALM_NAME}} -l 12h
service cron start
(crontab -l 2>/dev/null; echo '0 */11 * * * kinit -kt /var/practicus/{{USER_NAME}}.keytab {{USER_NAME}}@{{REALM_NAME}} -l 12h') | crontab -
sh /var/practicus/.practicus/entry.sh
```

Running this command outputs the `base64` encoded string you'll use. This method allows the entire script, including newlines and special characters, to be safely stored and then decoded back to its original form for execution.

## Running the Startup Script to Create Keytab and Initial Ticket

In this step, we'll use the provided `base64` encoded command to create and run a startup script. This script will create the keytab file, obtain your initial Kerberos TGT (Ticket Granting Ticket), and set up the cron job automatically.

**Critical Security Warning** 

The `base64` encoded string you'll use contains your Kerberos password in plain text within the script it decodes. This is a significant security risk. You should only use this method for testing or in highly controlled, secure environments. Never pass passwords in this manner in production environments or when dealing with sensitive data. The preferred and secure method is always to use a keytab securely generated and distributed by a Kerberos administrator.

Now, execute the following command in your terminal. Before running, replace the placeholders `{{USER_NAME}}`, `{{REALM_NAME}}`, and `{{PASSWORD}}` in the `base64` string with your actual Kerberos username, realm name, and password, respectively. 

```bash
base64 --decode <<< "...add your base64 encoded script here..." > /var/practicus/lib-install.sh && chmod +x /var/practicus/lib-install.sh && sh /var/practicus/lib-install.sh
```

**Explanation of this Command Chain**

This single command line performs a sequence of operations:

1.  `base64 --decode <<< "..."`: This part decodes the provided `base64` encoded string. The decoded string is actually a multi-line shell script containing all the setup steps.
2.  `> /var/practicus/lib-install.sh`: The output from the `base64 --decode` command (which is our decoded shell script) is then redirected and written into a file named `/var/practicus/lib-install.sh`.
3.  `&& chmod +x /var/practicus/lib-install.sh`: The `&&` operator ensures that this command runs *only if* the previous command (writing the script to the file) was successful. `chmod +x` then grants executable permissions to the newly created script file, making it runnable.
4.  `&& sh /var/practicus/lib-install.sh`: Again, using `&&`, this command runs the script we just created and made executable. The `sh` command executes the script using the system's default shell.


## Monitoring and Verification

After the setup is complete, it's crucial to verify that everything is working as expected. These verification steps should be performed directly within the relevant Kubernetes pod (e.g., apphost, modelhost, or worker pod) where your application or process requiring Kerberos authentication is running. 

**Checking Kerberos Ticket Status**

You can manually check the validity and expiration time of your current Kerberos ticket using the `klist` command:

```bash
klist -f
```

In the output, you should see *Valid starting* and *Expires* times. After the `cron` job runs, you'll notice that the "Expires" time has been extended.

**Checking Crontab Entry**

To confirm that the cron job has been added correctly, you can list your `crontab` entries:

```bash
crontab -l
```

You should see a line similar to `0 */11 * * * kinit -kt /var/practicus/{{USER_NAME}}.keytab {{USER_NAME}}@{{REALM_NAME}} -l 12h` in the output.

## Conclusion

By following these straightforward steps, you've successfully automated the process of creating a Kerberos keytab file, obtaining an initial ticket, and setting up `cron` to automatically renew your Kerberos tickets. This setup ensures continuous access to your Kerberos-authenticated services, significantly enhancing the reliability of your automated processes and reducing the need for manual intervention.

---

**Previous**: [Work With Connections](work-with-connections.md) | **Next**: [Integrate Git](integrate-git.md)
