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

Practicus AI cloud worker nodes can start and stop with a click using our app, and they run in your Amazon Web Services (AWS) cloud account in a fully isolated fashion. This way we can offer you 100% privacy. 

If you do not have an AWS account already, please click <a href="https://aws.amazon.com/" target="_blank">here</a> to create a one for **free**. Please check the <a href="https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/" target="_blank">AWS help page</a> if you need assistance on creating an account. AWS free tier offers t3.micro and our free software matches the same capacity.

### Enabling AWS marketplace

This is a **one-time task for all users** sharing the same AWS Account. New to AWS marketplace? Please click [here](#aws-marketplace) to learn more. 

We have multiple offerings on AWS marketplace. Please click on each in the below list to view the marketplace page explaining the offering, and then click **Continue to Subscribe** button to enable (see screenshot below). If in doubt, you can pick the first regular offering and safely ignore the rest **or** enable them all in one go in case you ever need them.  

Please note that it can take a few minutes for the offering to be active. Once your subscription is active please do **not** create a new EC2 instance using AWS cloud console. Continue with the below activation step instead.   

#### Regular PAYG (pay-as-you-go) AWS Marketplace offerings

- <a href="https://aws.amazon.com/marketplace/pp?sku=92p0y3k5wuzzfhi71lmcigl5q" target="_blank">Practicus AI</a> - Most common, offers free tier, will give you all of the functionality.
- <a href="https://aws.amazon.com/marketplace/pp?sku=84fu9xjxpikj0pw37w8zchum" target="_blank">Practicus AI with GPUs</a> - Accelerated computing for very large data **or** if you have limited time. Can be 500+ times faster for some operations. 

#### Enterprise License BYOL (bring-your-own-license) AWS Marketplace offerings
- <a href="https://aws.amazon.com/marketplace/pp?sku=5imq5zmm3najdjy989wuoytjo" target="_blank">Practicus AI</a> - Most common enterprise offer
- <a href="https://aws.amazon.com/marketplace/pp?sku=3o0d18rnipiqy9isz9aw1fsrv" target="_blank" rel="noopener">Practicus AI with GPUs</a> - Accelerated computing, enterprise offer


<div style="text-align: center;">Sample view of our AWS marketplace page</div>
![AWS Marketplace](img/aws-mp.png)

### Registering AWS user 

Simply open the Practicus AI app, go to settings (preferences in macOS), cloud tab and enter your AWS user credentials. The AWS account needs one or more of our [AWS marketplace](#enabling-aws-marketplace) offerings enabled. 


## References

### AWS Marketplace

Similar to our Windows app being available on Microsoft app store, our cloud worker nodes are available on AWS marketplace. This gives our users "there's an app for that!" type experience, but for AI in the cloud. 

Any time you need to do AI in the cloud, you can just click a button in the Practicus AI app, and we will create the cloud capacity of your choice. And also shut it down with a click when you no longer need it, saving on cost.,

For our app to be able to start/stop cloud worker nodes you need to enable (subscribe to) the AWS marketplace offering of your choice. 

If you use the free tier (t3.micro) with 2 vCPUs and 1 GB RAM, there won't be any charges. 
AWS will charge you for larger capacity **per hour.** i.e. you start a cloud worker, use it for 2 hours and never use it again. Your cloud bill will have a line item for the 2 hours you use. Larger capacity is more expensive and the larger the capacity the bigger discount you will get. Please click below 

### Linux Installation
If you are a Python user you can enjoy the below scripts.  


### Python Setup Guide
If you are a Python user you can enjoy the below scripts.  

