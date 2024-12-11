# Next Steps

Congrats on completing Practicus AI Studio tutorial!

There are still many topics that we haven't covered in our tutorial, and we will be adding sections about these in the near future. So please be on the lookout.

Please feel free to experiment with these features yourself, since many of them are very intuitive to use.

We have several videos where you can learn about Practicus AI. Please view them on the [Demo Videos](https://practicus.ai/demo/) section.

Some topics we haven't covered are:

## Advanced Data Preparation

- Joins: You can join any data, from **different data sources.** E.g. You can join data on S3 to data on a relational database. Please view the [join help page](../join.md) in our documentation to learn more. 
- Handling missing values
- Machine learning related tasks

## Excel Prep

If you work with someone who doesn't use Practicus AI, you can share any data over Excel / Google Sheets with them, so they can make changes and send back to you. You can then detect their changes and apply as steps to _any_ data.

Please view [Excel prep help page](../excel-prep.md) to learn more

## Python Coding

You can use the built-in Python editor in Practicus AI app to extend for any functionality. This feature doesn't require the cloud and the app comes with all the relevant libraries pre-installed such as pandas, and requests for API calls.

## Deployment to production

Once you finish preparing your data, building models, making predictions, and other tasks, you can automate what you have designed, so it can run automatically on a defined schedule such as every night or every week.

Please view the following pages to learn more:

- [Code Export (Deploy)](../code-export.md)
- [Airflow Integration](../airflow.md)
- [Modern Data Pipelines](../modern-data-pipelines.md)

## Observability

Please view [logging help page](../logging.md) to learn more.

## GPU Acceleration

You can choose to use GPU powered Cloud Workers by simply selecting _Accelerated Computing_ family while launching a Cloud Worker. 


## Data Processing Engines

If you are a technical user, you can choose an engine of your choice, including pandas, DASK, RAPIDS, RAPIDS+DASK and SPARK. Simply click the _Advanced_ button before loading data. 

## Advanced Sampling

If you work with very large data, you can load a different sample size on the Cloud Worker. E.g. original data source can be 1 billion rows, you can read 200 million on the cloud and 1 million on the app. Simply click the _Advanced_ button before loading data.      

This concludes our tutorial. Thank you for reading!

[< Previous](chatgpt.md)