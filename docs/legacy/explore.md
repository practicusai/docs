Up to 100+ times faster sampling. Random sample 1 billion+ rows down to 1 million in only a few seconds. 
Switch between data engines if you need (Pandas, DASK, Spark, GPUs with RAPIDS). 
Use S3 like a local drive on your laptop by simple copy/paste operations. Query Databases using SQL.

## Local Files

You can browse local files in the Explore tab and preview the data you want to work with easily.

![local_files](img/local_files.png)

You can create a new file, copy and paste the files on Cloud Worker or S3

## Cloud Worker Files

Firstly you have to launch a new Cloud Worker from the Cloud Tab. Then you can navigate the Cloud Worker content. You can preview the file by clicking on it.

![cloud_node_files](img/cloud_node_files.png)

### Create Folder
Let's create a new folder.

![create_folder](img/create_folder.png)

![create_folder2](img/create_folder2.png)

A new folder has been created.

You can also download and upload files on Cloud Worker and run the necessary scripts for databases.

### Upload
A directory is selected for the upload process.

![upload](img/upload.png)

You can select the file you want to upload from the file dialog.

![upload2](img/upload2.png)

After making your selection, you will be directed to the file transfer tab.

![file_transfer](img/file_transfer.png)

It starts the process with start transfer and you can close the tab when the process is finished.

![file_transfer2](img/file_transfer2.png)

You can see the uploaded file by navigating on Cloud Worker.

![upload3](img/upload3.png)

### Download

Select the files and start the download process.

![download](img/download.png)

![download2](img/download2.png)

After completing the download via the file transfer tab, you can navigate to local files and find the file.

![download3](img/download3.png)

## Amazon S3

After the required Cloud Config setup process is completed, you can load the buckets with Amazon S3, then select the bucket and navigate the files.
Note : For this operation you need ready Cloud Worker.

![amazons3](img/amazons3.png)

You can also perform the features (copy, paste, upload, download, new folder) in the menu bar.

## Relational Databases

You can connect to the database using relational databases, run SQL queries, and continue your operations on the data.
Amazon Redshift, Snowflake, PostgreSQL, MySQL, SQLite, Amazon Athena, Hive(Hadoop), SQLServer, Oracle, ElasticSearch, AWSOpenSearch, OtherDB connections are supported.
Amazon Athena, Hive(Hadoop), SQLServer, Oracle, ElasticSearch, AWSOpenSearch databases need driver installation.

Note: You need a ready Cloud Worker to access Relational Databases.

![mysql](img/mysql.png)

