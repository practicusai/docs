---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Bank marketing Sample
A banking company wants to develop a model to predict the customers who will subscribe to time deposits and also wants to reach customers who are likely to subscribe to time deposits by using the call center resource correctly.

In the data set to be studied, variables such as demographic information, balance information and previous campaign information of the customers will be used to predict whether they will subscribe to time deposits.

**Using the App**
- You can open the dataset in the Practicus AI  by loading all data
- Then in the analysis phase, you can start with profiling the data
- Then Graph > Boxplot > Age
- Groupby > Age, Job,  Balance Mean & Median
- Analyze > Graph > Plot -> Job -> Balance Mean Add Layer, Balance Median Add Layer

**Using Notebook**
- You can find detailed preprocessing steps in the notebook made with SDK
- The main idea here is that the model is built by filtering the -1s in the pdays variable, that is, they are not included in the model.
- In addition, the poutcome variable should be deleted to prevent Data Leakage.
- Then the model Feature Selection was selected as 95% and the Setup params were set to fix_imbalance: True.

```python
import practicuscore as prt

worker = prt.get_local_worker()
```

```python
data_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/bank_marketing.csv"
}

proc = worker.load(data_conn) 
proc.show_head() 
```

```python
proc.delete_columns(['poutcome']) 
```

```python
proc.run_snippet( 
    'one_hot', 
    text_col_list=['marital', 'default', 'housing', 'loan', ],  
    max_categories=25,  
    dummy_option='Drop First Dummy',  
    result_col_suffix=[],  
    result_col_prefix=[],  
) 
```

```python
proc.delete_columns(['default']) 
```

```python
proc.delete_columns(['housing', 'loan']) 
```

```python
proc.delete_columns(['marital']) 
```

```python
proc.run_snippet( 
    'label_encoder', 
    text_col_list=['job', 'education', 'contact', 'month', 'deposit', ],  
) 
```

```python
filter_expression = ''' 
col[pdays] != -1 
''' 
proc.filter(filter_expression) 
```

```python
proc.wait_until_done()
proc.show_logs()
```

```python
df = proc.get_df_copy()
display(df)
```

#### Building a model using AutoML

The below code is generated. You can update the code to fit your needs, or re-create it by building a model with Practicus AI app first and then view it's jupter notebook oncethe model building is completed.

```python
from pycaret.classification import ClassificationExperiment, load_model, predict_model

exp = ClassificationExperiment()
```

```python
experiment_name = 'Bank-marketing'
experiment_tracking_service = None
assert experiment_tracking_service, "Please select an experiment tracking service, or skip this cell"
prt.experiments.configure(service_name=experiment_tracking_service, experiment_name=experiment_name)
```

```python
setup_params = {'fix_imbalance': True}
```

```python
exp.setup(data=df, target='deposit', session_id=7272, 
          log_experiment=True, experiment_name=experiment_name, **setup_params)
```

```python
best_model = exp.compare_models()
```

```python
tune_params = {}
```

```python
tuned_model = exp.tune_model(best_model, **tune_params)
```

```python
final_model = exp.finalize_model(tuned_model)
```

```python
predictions = exp.predict_model(final_model, data=df)
display(predictions)
```

```python
exp.save_model(final_model, 'model')
```

```python
loaded_model = load_model('model')

predictions = predict_model(loaded_model, data=df)
display(predictions)
```

```python
deployment_key = None
assert deployment_key, "Please select a deployment key"
prefix = 'models'
model_name = 'my-bank-marketing-model'
model_dir = None  # Current dir
```

```python
# Deploy to current Practicus AI region
prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=model_dir
)
```

#### Prediction by using model API

```python
region = prt.current_region()

# *All* Practicus AI model APIs follow the below url convention
api_url = f"{region.url}/{prefix}/{model_name}/"
# Important: For effective traffic routing, always terminate the url with / at the end.
print("Model REST API Url:", api_url)
```

```python
# We will be using using the SDK to get a session token.
# To learn how to get a token without the SDK, please view 05_others/tokens sample notebook
token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

```python
import requests 
import pandas as pd

headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'text/csv'
}
data_csv = df.to_csv(index=False)

r = requests.post(api_url, headers=headers, data=data_csv)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

from io import BytesIO
pred_df = pd.read_csv(BytesIO(r.content))

print("Prediction Result:")
pred_df.head()
```

#### Prediction by using SDK

```python
proc.predict( 
    api_url='https://dev.practicus.io/models/my-bank-marketing-model/', 
    column_names=['age', 'job', 'education', 'balance', 'contact', 'day', 'month',
        'duration', 'campaign', 'pdays', 'previous','marital_married', 
        'marital_single', 'default_yes', 'housing_yes','loan_yes'], 
    new_column_name='predicted_deposit' 
) 
```

```python
df_predicted = proc.get_df_copy()
```

```python
df_predicted['predicted_deposit'].head()
```

```python
proc.kill()
```


## Supplementary Files

### snippets/label_encoder.py
```python
def label_encoder(df, text_col_list: list[str] | None = None):
    """
    Applies label encoding to specified categorical columns or all categorical columns in the dataframe if none are specified.
    :param text_col_list: Optional list of column names to apply label encoding. If None, applies to all categorical columns.
    """
    from sklearn.preprocessing import LabelEncoder

    le = LabelEncoder()

    # If text_col_list is provided, use it; otherwise, select all categorical columns
    if text_col_list is not None:
        categorical_cols = text_col_list
    else:
        categorical_cols = [col for col in df.columns if col.dtype == 'O']

    # Apply Label Encoding to each specified (or detected) categorical column
    for col in categorical_cols:
        # Check if the column exists in the DataFrame to avoid KeyError
        if col in df.columns:
            df[col] = le.fit_transform(df[col])
        else:
            print(f"Warning: Column '{col}' not found in DataFrame.")

    return df


label_encoder.worker_required = True

```

### snippets/one_hot.py
```python
from enum import Enum


class DummyOption(str, Enum):
    DROP_FIRST = "Drop First Dummy"
    KEEP_ALL = "Keep All Dummies"


def one_hot(df, text_col_list: list[str] | None,
            max_categories: int = 25, dummy_option: DummyOption = DummyOption.KEEP_ALL,
            result_col_suffix: list[str] | None = None, result_col_prefix: list[str] | None = None):
    """
    Applies one-hot encoding to specified columns in the DataFrame. If no columns are specified,
    one-hot encoding is applied to all categorical columns that have a number of unique categories
    less than or equal to the specified max_categories. It provides an option to either drop the
    first dummy column to avoid multicollinearity or keep all dummy columns.

    :param text_col_list: List of column names to apply one-hot encoding. If None, applies to all
                          suitable categorical columns.
    :param max_categories: Maximum number of unique categories in a column to be included for encoding.
    :param dummy_option: Specifies whether to drop the first dummy column (DROP_FIRST) or keep all
                         (KEEP_ALL).
    :param result_col_suffix: Suffix for the new column where the suppressed data will be stored.
    :param result_col_prefix: Prefix for the new column where the suppressed data will be stored.
    """
    import pandas as pd

    if text_col_list is None:
        text_col_list = [col for col in df.columns if df[col].dtype == 'object' and df[col].nunique() <= max_categories]

    for col in text_col_list:
        dummies = pd.get_dummies(df[col], prefix=(result_col_prefix if result_col_prefix else col),
                                 drop_first=(dummy_option == DummyOption.DROP_FIRST))
        dummies = dummies.rename(columns=lambda x: f'{x}_{result_col_suffix}' if result_col_suffix else x)

        df = pd.concat([df, dummies], axis=1)

    return df

```


---

**Previous**: [Shap Analysis](../shap-analysis.md) | **Next**: [Generative AI > Email E Asistant > Mail E-Assistant](../../generative-ai/email-e-asistant/mail-e-assistant.md)
