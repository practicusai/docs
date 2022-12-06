# Modeling with AutoML

_This section requires a Practicus AI cloud node. Please visit the [introduction to cloud nodes](worker-node-intro.md) section of this tutorial to learn more._

## Loading Insurance dataset

- Open _Explore_ tab
- Select a _Cloud Node_ upper right of screen (start new or reuse existing)
- Select _Cloud Node Files_ 
- Navigate to Home > samples > insurance.csv and _Load_ 
- Click _Model_ button

![](img/model/model-1.png)

- View the below optional sections, and then click ok to build the model

## (Optional) Building Excel Model

By default, models you build can be consumed using Practicus AI app or any other AI system. If you would like to build an Excel model, please do the following. Please note that this feature is not available for the free cloud tier.

- In the _Model_ dialog click on _Advanced Options_
- Select _Build Excel model_ and enter for how many rows, such as 1500

## (Optional) Explaining Models

If you would like to build graphics that explain how your model works, please do the following. Please note that the free tier cloud capacity can take a long time to build these visualizations.  

- In the _Model_ dialog click on _Advanced Options_
- Select _Explain_

If you choose the optional sections, model dialog should look like the below:  

![](img/model/model-2.png)

- Click ok to start building the model

You should see a progress bar at the bottom building the model. 

![](img/model/model-3.png)

For a fresh cloud node with regular size (2 CPUs) the first time you build this model it should take 5-10 minutes to be completed. Subsequent model runs will take less time. Larger cloud nodes with more capacity build models faster and more accurately.  

After the model build is completed you will see a dialog like the below.

![](img/model/model-4.png)

- Select all the options
- Click ok

If you requested to build an Excel model, you will be asked if you want to download. 

![](img/model/model-download-excel.png)

We will make predictions in the next section using these models, or models that other built. 

## (Optional) Reviewing Model Experiment Details

If you chose to explain how the model works: 

- Click on the _MLflow_ tab
- Select _explain_ folder at the left menu 
- Navigate to relevant graphics, for instance _Feature Importance_

![](img/model/model-explain.png)

The above tells us that an individual not being a smoker (smoker = 0), their bmi, and age are the most defining features to predict the insurance charge they will pay.

Note: You can always come back to this screen later by opening _CLoud Nodes_ tab, clicking on MLflow button and finding the experiment you are interested with. 

## (Optional) Downloading model experiment files

You can always download model related files, including Excel models, Python binary models, Jupyter notebooks, model build detailed logs, and other artifacts by going back to Explore tab and visiting Home > models

You can then select the model experiment you are interested, and click download  

![](img/model/model-download-artifacts.png)

## (Optional) Saving Models to a central database 

In the above steps, the model we built are stored on a cloud node and will disappear if we delete the cloud node without downloading the model first. This is usually ok for an ad-hoc experimentation. A better alternative can be to configure a central MLflow database, so your models are visible to others, and vice versa, you will be easily find theirs. We will visit this topic later.    




[< Previous](data-profiling.md) | [Next >](predict.md)