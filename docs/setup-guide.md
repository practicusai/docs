Welcome! Overall, it should take **~5 minutes for you to set up everything** and be ready to go!

Some information in this guide is for advanced scenarios, and you can safely ignore them if you prefer to keep it simple. 

## Installing Practicus AI app

If you haven't already, please install Practicus AI app for [Windows](https://www.microsoft.com/en-us/p/practicus-ai/9p9f4hvkvcqg), [macOS](https://github.com/practicusai/app/releases/download/latest/practicus.pkg) or [Linux](#linux-installation).  

If you are a Python user and prefer to install Practicus AI as a library, please check our [Python Setup Guide](#python-setup-guide) section below. 

## Cloud Activation

Some of our advanced features require cloud worker nodes. You can activate the cloud capacity in a few minutes and use the **forever free cloud tier** using **2 vCPUs and 1 GB RAM**. For larger capacity, you can **pay-as-you-go hourly** without giving us your credit card info or making any commitments. 

Your organization can also acquire an **unlimited license for multiple users and with a fixed fee**. Please contact [sales](mailto:sales@practicus.ai?subject=Enterprise License) to learn more about our enterprise support and licensing.

### Creating an AWS account

Please skip this step if you already have an AWS account. 

This is a **one-time task for all users** sharing the same AWS Account. If you do not have an AWS account already, please <a href="https://aws.amazon.com/" target="_blank">click here</a> to create a one for **free**. 

Please make sure you have created an **admin user** as well. You can check our [AWS account creation guide below](#aws-account-creation) for help.


### Enabling AWS marketplace

This is a **one-time task for all users** sharing the same AWS Account. New to AWS marketplace? Please click [here](#aws-marketplace) to learn more. 

We have multiple offerings on AWS marketplace. Please click on each in the below list to view the marketplace page explaining the offering, and then click **Continue to Subscribe** button to enable (see screenshot below). If in doubt, you can pick the first regular offering and safely ignore the rest **or** enable them all in one go in case you ever need them.  

Please note that it can take a few minutes for the offering to be active. Once your subscription is active please do **not** create a new EC2 instance using AWS cloud console. Continue with the below activation step instead.   

#### Regular PAYG (pay-as-you-go) 

- <a href="https://aws.amazon.com/marketplace/pp?sku=92p0y3k5wuzzfhi71lmcigl5q" target="_blank">Practicus AI</a> - Most common, offers free tier, will give you all of the functionality.
- <a href="https://aws.amazon.com/marketplace/pp?sku=84fu9xjxpikj0pw37w8zchum" target="_blank">Practicus AI with GPUs</a> - Accelerated computing for very large data **or** if you have limited time. Can be 500+ times faster for some operations. 

#### Enterprise License BYOL (bring-your-own-license)
- <a href="https://aws.amazon.com/marketplace/pp?sku=5imq5zmm3najdjy989wuoytjo" target="_blank">Practicus AI</a> - Most common enterprise offer
- <a href="https://aws.amazon.com/marketplace/pp?sku=3o0d18rnipiqy9isz9aw1fsrv" target="_blank" rel="noopener">Practicus AI with GPUs</a> - Accelerated computing, enterprise offer


<div style="text-align: center;">Sample view of our AWS marketplace page</div>
![AWS Marketplace](img/aws-mp.png)

### Registering AWS user 

Simply open the Practicus AI app, go to settings (preferences in macOS), cloud tab and enter your AWS user credentials. The AWS account needs one or more of our [AWS marketplace](#enabling-aws-marketplace) offerings enabled. 


## References

### AWS Account Creation
Practicus AI cloud worker nodes can start and stop with a click using our app, and they run in your Amazon Web Services (AWS) cloud account in a fully isolated fashion. This way we can offer you 100% privacy. 

Please follow the below steps to create a **free** AWS account.

1. Please <a href="https://aws.amazon.com/" target="_blank">click here</a> to visit AWS home page and click _Create an AWS account_
2. Follow the steps to finish account creation. Please check the <a href="https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/" target="_blank">AWS help page</a> if you need assistance on creating an account. After this step you will have a root account.
3. Login to <a href="https://aws.amazon.com/console/" target="_blank">AWS management console</a> using your root account. 
4. Navigate to IAM (Identity and Access Management), click Users on the left menu and click _Add users_
5. For User name enter **admin**, click Access key and Password check boxes (see below screenshot)
6. In Set permissions section select _Attach existing policies directly_ and pick _AdministratorAccess_ (see below screenshot)
7. In the last screen carefully save you **Access Key ID**, **Secret access key** and Password (see below screenshot)
8. All done! You can continue with the next step, [Enabling AWS marketplace](#enabling-aws-marketplace) 

**Note:** Although the admin AWS user will be sufficient for Practicus AI cloud nodes to run, as a security best practice we recommend you to create a least privileged AWS user for day to day usage. Practicus AI app cloud setup can create this user for you. If you rather prefer to create one manually please make sure the user has access for EC2 and S3 operations. If you will have multiple users sharing the same account, you can simply add new users to the practicus AWS user group that the app creates for you. 

_Screenshots_
![aws account creation step 1](img/add_aws_user_1.png)

![aws account creation step 2](img/add_aws_user_2.png)

![aws account creation step 3](img/add_aws_user_3.png)

### AWS Marketplace

Similar to our Windows app being available on Microsoft app store, our cloud worker nodes are available on AWS marketplace. This gives our users "there's an app for that!" type experience, but for AI in the cloud. 

Any time you need to do AI in the cloud, you can just click a button in the Practicus AI app, and we will create the cloud capacity of your choice. And also shut it down with a click when you no longer need it, saving on cost.,

For our app to be able to start/stop cloud worker nodes you need to enable (subscribe to) the AWS marketplace offering of your choice. 

If you use the free tier (t3.micro) with 2 vCPUs and 1 GB RAM, there won't be any charges. 
AWS will charge you for larger capacity **per hour.** i.e. you start a cloud worker, use it for 2 hours and never use it again. Your cloud bill will have a line item for the 2 hours you use. Larger capacity is more expensive and the larger the capacity the bigger discount you will get. Please click below 

### Linux Installation
Since almost all Linux distros come with Python 3 installed, we do not offer a prepackaged installer. 

Please check the quick start guide [below](#macos-or-linux-quickstart) to see how you can install and run Practicus AI app on Linux. We have extensively tested on Ubuntu, if you encounter any issues please share with us using [feedback](feedback.md) section.


### Python Setup Guide
You can run **pip install practicus** (Windows/macOS: Python 3.7 – 3.10, Linux: 3.8 – 3.10) and then run **practicus** from the terminal. Or run, python -c “import practicus; practicus.run()”  (python3 for macOS or Linux).

Installing using pip will give you the exact same end-to-end GUI application experience. Similarly, if you download the packaged app you can still code freely when you want to. So, please select any method of installation as you prefer. 

As for any Python application, we strongly recommend you to use a virtual environment such as venv or conda. Please check the recommended QuickStart scripts on this page to create a virtual env, install Practicus AI and run with peace of mind and in one go.  

For server environments or API only usage, you can **pip install practicuscore** to install the core library by itself without the GUI elements. (Linux: Python 3.6 – 3.10, Windows/macOS: Python 3.7 – 3.10) 

This is a small library with fewer requirements and no version enforcement for any of its dependencies. It’s designed to run in existing virtual environments without overriding the version requirements of other libraries. Please check the documentation for more details. 

#### Windows QuickStart
```shell
:: install 
python -m venv %UserProfile%\practicus\venv
%UserProfile%\practicus\venv\Scripts\python -m pip install --upgrade practicus


:: run
%UserProfile%\practicus\venv\Scripts\activate
practicus
```

#### Macos or Linux QuickStart
```shell
# install
python3 -m venv ~/practicus/venv 
~/practicus/venv/bin/python -m pip install --upgrade practicus


# run
source ~/practicus/venv/bin/activate
practicus
```

### Starter app
Instead of running Practicus AI from the command prompt (terminal) you can create shortcuts and run with double click. The below tips assume you installed using the QuickStart tips above.

**Windows:** Navigate to ** %UserProfile%\practicus\venv\Scripts\ ** folder and locate practicus.exe, which is essentially a starter for practicus Python library. You can right-click and select pin to start. You can also create a shortcut to this .exe and change its name to Practicus AI and its icon by downloading our icon [practicus.ico](https://github.com/practicusai/app/raw/main/practicus.ico). 

**macOS:** You can download [Practicus AI Starter app](https://github.com/practicusai/app/raw/main/practicus_starter.pkg) which is a tiny (100KB) app that starts the Python virtual env in ** ~/practicus/venv ** and then starts Practicus AI GUI from practicus Python library. To keep the app in dock please drag & drop the .app file on the dock itself. Right-clicking and choosing “keep in dock” will not create a shortcut.

