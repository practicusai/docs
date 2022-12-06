# Introduction to Practicus AI Worker Nodes

Some advanced Practicus AI features require to use software in addition to Practicus AI APP or the developer SDK. In this section we will learn how to use Practicus AI Worker Nodes.

## What is a Worker Node?

Some Practicus AI features such as **AutoML**, making ** AI Predictions**, **Advanced Profiling** and **production deployment** capabilities require a larger setup, so we moved these from the app to a backend (server) system.  

You have multiple Worker Node options to choose from. You can run them in the cloud or on your computer. Please view [help on choosing a Worker Node](../setup-guide.md#choose-a-worker-node-system) to learn more.  


## Setup Worker Node

Please check the [Setup Guide](../setup-guide.md) to learn how to configure Practicus AI Worker Nodes. 

You can use the free cloud tier for this tutorial, or use containers on your computer as well.

## Launching a new Worker Node

- Click on the _Cloud_ button to open the _Worker Nodes_ tab
- Make sure the selected local for your computer, or the optimal _AWS Cloud Region_. The closest region geographically will usually give you the best internet network performance
- Click _Launch New_ 

![](img/cloud-intro/cloud-tab.png)

- Pick the type (size) of your Worker Node
- Click ok to launch 

The default size will be enough for most tasks. You can also choose the free cloud tier.

![](img/cloud-intro/launch.png)

In a few seconds you will see your Worker Node is launching, and in 1-2 minutes you will get a message saying your Worker Node is ready.

![](img/cloud-intro/launch-2.png)

## Stopping a Worker Node

If you use local container Worker Nodes you have less to worry about stopping them.  

### Cloud Worker Nodes
Similar to electricity, water, or other utilities, your cloud vendor (AWS) will charge you a fee for the hours your Worker Node is running. Although Practicus AI Worker Nodes automatically shut down after 90 minutes, it would be a practical approach to shut down your Worker Nodes manually when you are done for the day.

For this, you can simply select a clod node and click on the _Stop_ button. The next day, you cna select the stopped Worker Node, click _Start_ and continue where you are left.

Tip: It is usually not a good idea to frequently stop / start instances. Please prefer to stop if your break is at least a few hours for optimal cost and wait time.

## Terminating a Worker Node

Practicus AI Worker Nodes are designed to be disposable, also called ephemeral. You can choose a Worker Node and click _Terminate_ to simply delete everything related to it.

Please be careful that if you choose to store data on the local disk of your Worker Node, this will also get lost after termination. In this case, you can prefer to copy your data manually, or simply click the _Replicate_ button before terminating a Worker Node. 

## (Optional) Using Jupyter Lab

For technical users.

Every Worker Node comes with some external services preconfigured, such as Jupyter Lab, Mlflow, Airflow.  

- Select a Worker Node that is running and ready
- Click on Jupyter button

This will start the Jupyter Lab service and view inside the app. You can also right-click tab name and select _Open in browser_ to view the notebook on your default browser.

![](img/cloud-intro/jupyter.png)

Notes: 

- If you shut down the app, the secure connection tunnel to the Worker Node notebook service will be lost even if the Worker Node continues to run.
- There are two separate Conda kernels configured for your notebook server. Big data one will have common libraries and data engines, such as DASK, RAPIDS (if you have GPUs) and Spark installed. The ML one, as the name suggests, will have ML related libraries such as scikit-learn, Xgboost, Pycaret ..

## (Optional) Using the Terminal

For technical users.

You can choose a Worker Node and click the _Terminal_ button to instantly open up the terminal. You have sudo (super-user) access and this can be a very powerful and flexible way to customize your Worker Node.

![](img/cloud-intro/terminal.png)


[< Previous](data-prep-intro.md) | [Next >](explore.md)