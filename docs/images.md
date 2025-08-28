# Practicus AI Worker Image Requirements

## Image: Practicus Core

The Practicus Core image is a comprehensive Python environment that includes essential data science libraries such as **pandas**, **numpy**, **scikit-learn**, **xgboost**, **dask**, and **mlflow**, enabling end-to-end workflows for data analysis, big data processing, machine learning, and MLOps.


<details>
<summary><strong>Packages</strong></summary>

| Package                 | Version   |
|-------------------------|-----------|
| ydata-profiling         | 4.16.1    |
| bokeh                   | 3.7.3     |
| xgboost                 | 3.0.3     |
| scikit-learn            | 1.7.1     |
| dask[dataframe]         | 2025.7.0  |
| distributed             | 2025.7.0  |
| dask-ml                 | -         |
| mcp                     | 1.12.3    |
| mlflow                  | -         |
| matplotlib              | -         |
| s3fs                    | -         |
| boto3                   | -         |
| jupyterlab-git          | -         |
| pymysql                 | -         |
| snowflake-sqlalchemy    | -         |
| oracledb                | -         |
| pyodbc                  | -         |
| pyarrow                 | -         |
| pyiceberg               | -         |
| polars                  | -         |
| neo4j                   | -         |
| pika                    | -         |
| ruff                    | -         |
| uv                      | -         |
| shap                    | -         |
| openai                  | -         |

</details>
---

## Image: Practicus Minimal

The Practicus Minimal image is a lightweight yet functional Python environment that includes essential libraries such as **pandas**, **pydantic**, and **sqlalchemy** for data processing and database connectivity, along with **jupyterlab** support for easily conducting data analysis and prototype development workflows.

<details>
<summary><strong>Packages</strong></summary>

| Package               | Version |
|-----------------------|---------|
| pandas                | 2.2.3   |
| pydantic              | 2.11.7  |
| duckdb                | 1.3.2   |
| PyJWT[crypto]         | 2.10.1  |
| websocket-client      | 1.8.0   |
| sqlalchemy            | 2.0.41  |
| aio-pika              | 9.5.5   |
| jupyterlab            | 4.4.5   |
| jinja2                | -       |
| joblib                | -       |
| cloudpickle           | -       |
| tornado               | -       |
| psutil                | -       |
| ipywidgets            | -       |
| jedi-language-server  | -       |
| psycopg2-binary       | -       |
| papermill             | -       |
</details>
---

## Image: Practicus GenAI

The Practicus GenAI image is optimized for developing large language model (LLM)-based applications, vector database integrations, and interactive AI solutions with libraries such as **streamlit**, **langchain**, **pymilvus**, **qdrant-client**, and **huggingface_hub**.

<details>
<summary><strong>Packages</strong></summary>

| Package                | Version |
|------------------------|---------|
| streamlit              | 1.47.1  |
| langchain[openai]      | -       |
| pymilvus               | 2.5.14  |
| qdrant-client          | 1.14.3  |
| langchain-community    | 0.3.27  |
| huggingface_hub        | 0.34.3  |
| psycopg2-binary        | 2.9.10  |
| psycopg[binary]        | 3.2.9   |
| asyncpg                | 0.30.0  |
| sqlmodel               | 0.0.24  |
| alembic                | 1.16.4  |
</details>
---

## Image: Practicus GenAI + Langflow

The Practicus GenAI + Langflow image is optimized for easily designing, testing, and running visual flow-based AI applications and LLM integrations using the **langflow** library.

<details>
<summary><strong>Packages</strong></summary>

| Package  | Version |
|----------|---------|
| langflow | 1.4.3   |
</details>
---

## Image: Practicus Spark

The Practicus Spark image is designed for large-scale data processing and analytics using **pyspark**, with **numpy** support for efficient numerical computations.

<details>
<summary><strong>Packages</strong></summary>

| Package  | Version |
|----------|---------|
| pyspark  | 3.5.6   |
| numpy    | -       |
</details>
---

## Image: Practicus Automl

The Practicus AutoML image is optimized for developing automated machine learning workflows, model training and tuning, evaluation, and explainable AI applications using libraries such as **pycaret**, **lightgbm**, **mlflow**, and other supporting packages.

<details>
<summary><strong>Packages</strong></summary>

| Package                        | Version |
|--------------------------------|---------|
| pycaret[models,parallel,tuners]| 3.3.2   |
| lightgbm                       | 3.3.5   |
| mlflow                         | 2.17.2  |
| interpret                      | -       |
| fairlearn                      | -       |
| prophet                        | -       |
| umap-learn                     | -       |
</details>
---

## Image: Practicus Ray

The Practicus Ray image is designed for distributed data processing, model training, hyperparameter optimization, and scalable AI application development using libraries such as **ray** and **modin**.

<details>
<summary><strong>Packages</strong></summary>

| Package                        | Version |
|--------------------------------|---------|
| ray[default,data,train,tune]   | -       |
| modin[ray]                     | -       |
</details>
---

## Image: Practicus Core GPU

The Practicus Core GPU image is a comprehensive, GPU-optimized Python environment for advanced data analysis, big data processing, and machine learning, featuring libraries such as **transformers**, **xgboost**, **scikit-learn**, **dask**, and **mlflow**, along with tools for visualization, database connectivity, distributed computing, and MLOps workflows.

<details>
<summary><strong>Packages</strong></summary>

| Package                 | Version  |
|-------------------------|----------|
| transformers            | -        |
| ydata-profiling         | 4.16.1   |
| bokeh                   | 3.7.3    |
| xgboost                 | 3.0.3    |
| scikit-learn            | 1.7.1    |
| dask[dataframe]         | 2025.7.0 |
| distributed             | 2025.7.0 |
| dask-ml                 | -        |
| mcp                     | 1.12.3   |
| mlflow                  | -        |
| matplotlib              | -        |
| s3fs                    | -        |
| boto3                   | -        |
| jupyterlab-git          | -        |
| pymysql                 | -        |
| snowflake-sqlalchemy    | -        |
| oracledb                | -        |
| pyodbc                  | -        |
| pyarrow                 | -        |
| pyiceberg               | -        |
| polars                  | -        |
| neo4j                   | -        |
| pika                    | -        |
| ruff                    | -        |
| uv                      | -        |
| shap                    | -        |
| openai                  | -        |
</details>
---

## Image: Practicus Minimal GPU

The Practicus Minimal GPU image is optimized for running data analysis, prototype development, and lightweight machine learning workflows on GPUs, featuring essential libraries such as **pandas**, **pydantic**, and **sqlalchemy**, along with **jupyterlab** support.

<details>
<summary><strong>Packages</strong></summary>

| Package               | Version |
|-----------------------|---------|
| pandas                | 2.2.3   |
| pydantic              | 2.11.7  |
| duckdb                | 1.3.2   |
| PyJWT[crypto]         | 2.10.1  |
| websocket-client      | 1.8.0   |
| sqlalchemy            | 2.0.42  |
| aio-pika              | 9.5.5   |
| jupyterlab            | 4.4.5   |
| jinja2                | -       |
| joblib                | -       |
| cloudpickle           | -       |
| tornado               | -       |
| psutil                | -       |
| ipywidgets            | -       |
| jedi-language-server  | -       |
| psycopg2-binary       | -       |
| psycopg[binary]       | -       |
| papermill             | -       |
</details>

---

## Image: Practicus Torch GPU

The Practicus Worker GPU + Torch image is optimized for deep learning development and training on GPUs, featuring **torch** for building and training neural networks and **transformers** for leveraging state-of-the-art NLP models.

<details>
<summary><strong>Packages</strong></summary>

| Package       | Version |
|---------------|---------|
| torch         | -       |
| transformers  | -       |
</details>

---

## Image: Practicus DeepSpeed GPU

The Practicus Worker GPU + DeepSpeed Base image is optimized for large-scale deep learning training and inference on GPUs, featuring **DeepSpeed** for distributed, memory-efficient training and **transformers** for working with state-of-the-art NLP models.

<details>
<summary><strong>Packages</strong></summary>

| Package       | Version |
|---------------|---------|
| deepspeed     | -       |
| transformers  | -       |
</details>

---

## Image: Practicus FairScale GPU

The Practicus Worker GPU + FairScale Base image is optimized for distributed and memory-efficient deep learning training on GPUs, featuring **FairScale** for advanced parallelization strategies and **transformers** for working with cutting-edge NLP models.

<details>
<summary><strong>Packages</strong></summary>

| Package       | Version |
|---------------|---------|
| fairscale     | -       |
| transformers  | -       |
</details>

---

## Image: Practicus Worker GPU + Whisper

The Practicus Worker GPU + Whisper image is optimized for speech-to-text and audio transcription tasks on GPUs, featuring **openai-whisper** for state-of-the-art speech recognition and including **ffmpeg** for handling a wide range of audio and video formats.

<details>
<summary><strong>Packages</strong></summary>

| Package         | Version |
|-----------------|---------|
| openai-whisper  | -       |
| ffmpeg*         | -       |
</details>

---

## Image: Practicus Ray GPU

The Practicus Ray GPU image is designed for distributed data processing, model training, hyperparameter optimization, and scalable AI application development on GPUs using libraries such as **ray** and **modin**.

<details>
<summary><strong>Packages</strong></summary>

| Package                        | Version |
|--------------------------------|---------|
| ray[default,data,train,tune]   | -       |
| modin[ray]                     | -       |
</details>


# Practicus AI Modelhost Image Requirements

---

## Image: Practicus Model Host

The Practicus Model Host image provides the foundational environment for deploying and serving machine learning models, featuring **FastAPI** and **Uvicorn** for high-performance API hosting, **scikit-learn** and **xgboost** for model execution, and a range of supporting libraries for data processing, caching, messaging, and observability.

<details>
<summary><strong>Packages</strong></summary>

| Package                | Version   |
|------------------------|-----------|
| fastapi                | 0.115.14  |
| uvicorn                | 0.34.3    |
| PyJWT[crypto]          | 2.10.1    |
| lz4                    | 4.4.4     |
| aiobotocore            | 2.21.1    |
| boto3                  | -         |
| prometheus-client      | 0.22.1    |
| aiofiles               | 24.1.0    |
| pydantic               | >2        |
| xgboost                | 2.1.4     |
| scikit-learn           | 1.6.1     |
| accumulation-tree      | 0.6.4     |
| beautifulsoup4         | -         |
| httpx                  | -         |
| websocket-client       | -         |
| requests               | -         |
| python-multipart       | -         |
| redis[hiredis]         | -         |
| confluent-kafka        | -         |
| pymemcache             | -         |
| joblib                 | -         |
| cloudpickle            | -         |
| neo4j                  | -         |
| pika                   | -         |
| pyyaml                 | -         |
</details>

---

## Image: Practicus Model Host AutoML

The Practicus Model Host AutoMLimage is optimized for serving automated machine learning models, featuring **PyCaret** for streamlined model training, tuning, and deployment workflows.

<details>
<summary><strong>Packages</strong></summary>

| Package                | Version |
|------------------------|---------|
| pycaret[models]        | 3.3.2   |
</details>

---

## Image: Practicus Model Host GPU

The Practicus Model Hosting GPU Base image is built for deploying and serving GPU-accelerated machine learning models, featuring **transformers** for working with state-of-the-art deep learning and natural language processing models, along with GPU-specific dependencies for high-performance inference.

<details>
<summary><strong>Packages</strong></summary>

| Package       | Version |
|---------------|---------|
| transformers  | -       |
</details>

---

## Image: Practicus Model Host GPU + Torch

The Practicus Model Hosting GPU + Torch image is optimized for deploying and serving GPU-accelerated deep learning models, featuring **torch** for building, training, and running neural networks in production environments.

<details>
<summary><strong>Packages</strong></summary>

| Package  | Version |
|----------|---------|
| torch    | -       |
</details>

---

## Image: Practicus Model Host GPU + VLLM

The Practicus Model Host GPU + VLLM image is optimized for high-throughput, low-latency large language model (LLM) inference on GPUs, featuring **vllm** for efficient model serving with advanced scheduling and memory optimization.

<details>
<summary><strong>Packages</strong></summary>

| Package | Version |
|---------|---------|
| vllm    | 0.9.1   |
</details>

---

## Image: Practicus Model Host GPU + vLLM + Tiny

The Practicus Model Host GPU + vLLM + Tiny image is preloaded with the **TinyLlama/TinyLlama-1.1B-Chat-v1.0** model for lightweight, high-speed LLM inference on small or legacy GPUs (e.g., Nvidia T4). It leverages **vLLM** for efficient serving and includes model files locally to enable fully offline operation.

<details>
<summary><strong>Preloaded Model</strong></summary>

| Model Name                                      | Precision | Notes                                      |
|-------------------------------------------------|-----------|--------------------------------------------|
| TinyLlama/TinyLlama-1.1B-Chat-v1.0              | half      | Optimized for small/legacy GPU deployment  |
</details>

---

## Image: Practicus Model Host Base LiteLLM

The Practicus Model Host Base LiteLLM image is tailored for running the LiteLLM proxy in production, enabling unified LLM routing and spend tracking with Prisma-based persistence and S3-compatible integrations.

<details>
<summary><strong>Packages</strong></summary>

| Package          | Version        |
|------------------|----------------|
| litellm[proxy]   | 1.74.3.post1   |
| aiobotocore      | <2.21.1        |
| prisma           | 0.11.0         |
</details>

---

## Image: Practicus Model Host SparkML Base

The Practicus Model Host SparkML Base image is designed for deploying and serving machine learning models built with Apache Spark MLlib, featuring **pyspark** for large-scale distributed data processing and machine learning.

<details>
<summary><strong>Packages</strong></summary>

| Package  | Version |
|----------|---------|
| pyspark  | 3.5.5   |
</details>


# Practicus AI App Image Requirements

---

## Image: Practicus App Hosting Base

The Practicus App Hosting Base image provides a versatile environment for deploying AI-powered applications, combining **FastAPI** and **Uvicorn** for high-performance APIs, **Streamlit** for interactive frontends, and **LangChain** with vector database clients for GenAI capabilities, along with broad support for databases, messaging, and caching.

<details>
<summary><strong>Packages</strong></summary>

| Package               | Version   |
|-----------------------|-----------|
| fastapi               | 0.116.1   |
| uvicorn               | 0.34.3    |
| aiobotocore           | 2.23.2    |
| boto3                 | -         |
| prometheus-client     | 0.22.1    |
| aiofiles              | 24.1.0    |
| aio-pika              | 9.5.5     |
| jinja2                | -         |
| httpx                 | -         |
| requests              | -         |
| openai                | -         |
| streamlit             | 1.47.1    |
| pymilvus              | 2.5.14    |
| qdrant-client         | 1.14.3    |
| langchain-community   | 0.3.27    |
| langchain_openai      | 0.3.28    |
| mcp                   | 1.12.3    |
| psycopg2-binary       | 2.9.10    |
| psycopg[binary]       | 3.2.9     |
| asyncpg               | 0.30.0    |
| sqlmodel              | 0.0.24    |
| alembic               | 1.16.4    |
| trino                 | 0.335.0   |
| sqlglot[rs]           | -         |
| beautifulsoup4        | -         |
| websocket-client      | -         |
| python-multipart      | -         |
| redis[hiredis]        | -         |
| confluent-kafka       | -         |
| pymemcache            | -         |
| neo4j                 | -         |
| pika                  | -         |
</details>

---

## Image: Practicus App Hosting Langflow Base

The Practicus App Hosting Langflow Base image is tailored for building and running visual, flow-based AI applications using **Langflow**, enabling easy integration and orchestration of LLMs and other AI tools within interactive workflows.

<details>
<summary><strong>Packages</strong></summary>

| Package   | Version |
|-----------|---------|
| langflow  | 1.4.3   |
</details>




