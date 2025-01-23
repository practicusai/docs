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

# API Triggers with HttpSensor in Apache Airflow

In this example, we will demonstrate how to use the `HttpSensor` in Apache Airflow to poll a REST API. This can be particularly useful if your pipeline depends on external API data or statuses.

## Overview
1. **Create or configure an Airflow Connection**: Under *Admin → Connections*, set up your HTTP connection (`Conn Id`) with the base URL and optionally store your token securely.
2. **Reference the connection in your DAG**: Use the `http_conn_id` in the `HttpSensor` (or define headers directly if you prefer).
3. **Set up your sensor**: The `HttpSensor` will regularly check (poke) an endpoint until it finds an expected value or times out.



## Example DAG
Below is a minimal example of a DAG using `HttpSensor`. When you place this code in an Airflow DAG file, it will:
- Start from `days_ago(1)`.
- Use the `HttpSensor` to GET from `my/api/endpoint`.
- Send an authorization Bearer token in the header.
- Check if the response contains `expected_value`. If yes, the task succeeds; if not, it keeps retrying until the timeout.


```python
from airflow.sensors.http_sensor import HttpSensor
from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id='example_http_sensor',
    default_args=default_args,
    schedule_interval='@once',
) as dag:

    http_sensor_task = HttpSensor(
        task_id='http_sensor_task',
        http_conn_id='my_http_conn_id',  # Must match the connection ID in Airflow
        endpoint='my/api/endpoint',
        method='GET',
        headers={
            'Authorization': 'Bearer YOUR_BEARER_TOKEN_HERE'
        },
        response_check=lambda response: "expected_value" in response.text,
        poke_interval=30,  # how often to ping the endpoint (in seconds)
        timeout=60,        # how long to wait before failing the task
        mode='reschedule'  # or 'poke' depending on your preference
    )

```

## Conclusion
By configuring an `HttpSensor` (or a custom sensor around `HttpHook`) with the correct headers, you can easily poll REST APIs that require Bearer tokens. This approach is handy for triggering downstream tasks only when external services have the data or status you need.


---

**Previous**: [Task Parameters](task-parameters.md) | **Next**: [Generative AI > Advanced LangChain > Lang Chain LLM Model](../generative-ai/advanced-langchain/lang-chain-llm-model.md)
