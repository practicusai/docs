---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Ice Cream Sales Revenue Prediction Model

This code builds, trains, and tests a linear regression model to predict ice cream sales revenue based on temperature data.


```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import practicuscore as prt

# Load data
data = pd.read_csv("/home/ubuntu/samples/data/ice_cream.csv")

# Split data
X = data[["Temperature"]]
y = data["Revenue"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)
```

# Displaying Actual vs. Predicted Revenue

This code creates a DataFrame to compare the actual and predicted ice cream sales revenue, then prints the first few rows.


```python
import pandas as pd

results_df = pd.DataFrame({"Actual Revenue": y_test.values, "Predicted Revenue": y_pred})

print(results_df.head())
```

# Saving the Trained Model

This code saves the trained linear regression model as a `.pkl` file using `pickle`, allowing it to be reused later without retraining.


```python
import pickle

# Save .pkl
model_file_path = "model.pkl"
with open(model_file_path, "wb") as file:
    pickle.dump(model, file)

print(f"Created '{model_file_path}'.")
```

# Creating and Extracting Model Archive

This code uses `prt.models.zip()` to create a compressed `model.zip` file containing supporting files (`support1.txt`, `support2.txt`), the script (`model.py`), and the trained model (`model.pkl`). The archive can be extracted later using `prt.models.unzip()`.



## Attention
- When you zip with prt, it zips the files given in the files_to_add parameter, but it does not zip the .pkl file because the pkl will already be in the same folder as the running notebook and when you deploy with prt, it will automatically deploy the pkl file, the purpose of the zip file is to contain auxiliary files inside.
- If your pkl file is in a different place or for a different reason, you can zip it yourself and put your pkl file in it, but there is a situation to be aware of, the pkl file should not be in any folder when you zip, if the zip file is unzipped, the pkl file does not appear when the zip file is unzipped, that is, if it is in another folder, you will get a .pkl not found error, the .pkl file should be directly visible when unzipped.
### Suggested Solutions
* If prt.models.zip is to be used, the “.pkl” file and the notebook where prt.models.deploy is running must be in the same directory so that when deployed, it deploys both the zip and the pkl file.
* If you want to zip with sh “zip -rj model.zip .../model/*”

```python
# Create model.zip

prt.models.zip(
    files_to_add=["support1.txt", "support2.txt", "model.py", "model.pkl"],
    model_dir=None,  # Current directory
)

# Unzip included with prt.models.unzip()
```

# Listing and Selecting a Model Deploy Params

This code retrieves available model prefixes from the current region, displays them as a Pandas DataFrame, and selects the first prefix for deployment. It also lists available model deployments and selects the second deployment key for further use.


```python
region = prt.get_region()
```

```python
# Let's list our model prefixes and select one of them.
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())

# We will select first prefix
model_prefix = my_model_prefixes[0].key
print("Using first prefix:", model_prefix)
```

```python
model_name = "test-zip-new"
```

```python
model_deployment_list = region.model_deployment_list
display(model_deployment_list.to_pandas())
deployment_key = region.model_deployment_list[1].key
```

# Deploying the Model

This code uploads `model.zip` using `prt.models.deploy()`, associating it with the selected deployment key and model prefix. The model is stored under the specified `model_name`, ready for deployment.


```python
# This will now upload model.zip
prt.models.deploy(deployment_key=deployment_key, prefix=model_prefix, model_name=model_name, model_dir=None)
```

# Generating Model API URL and Session Token

This code constructs the REST API URL for the deployed model using the region, model prefix, and model name. It then retrieves a session token using the Practicus AI SDK, which is required for authentication when interacting with the model API.


```python
# Practicus AI model APIs follow the below url convention
api_url = f"{region.url}/{model_prefix}/{model_name}/"
print("Model REST API Url:", api_url)
```

```python
# We will be using using the SDK to get a session token.
# To learn how to get a token without the SDK, please view 05_others/tokens sample notebook
token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

# Making Predictions via the Deployed Model API

This code sends a request to the deployed model API using the Practicus AI session token for authentication. It formats the input data (`X.head(10)`) as a CSV string and sends it via a POST request. The response, containing predictions, is read into a Pandas DataFrame for display.


```python
import requests

headers = {"authorization": f"Bearer {token}", "content-type": "text/csv"}
data_csv = X.head(10).to_csv(index=False)

r = requests.post(api_url, headers=headers, data=data_csv)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

from io import BytesIO

pred_df = pd.read_csv(BytesIO(r.content))

print("Prediction Result:")
pred_df.head()
```


---

**Previous**: [Bank Marketing](../bank-marketing/bank-marketing.md) | **Next**: [Workflows > Task Parameters](../../workflows/task-parameters.md)
