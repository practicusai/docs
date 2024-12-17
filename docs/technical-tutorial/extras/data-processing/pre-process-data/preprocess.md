---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (for ML)
    language: python
    name: practicus_ml
---

# Data Processing

## _Scenario:_ Pre-process steps by using SDK

In this example, we'll showcase how to apply pre-process steps by using our SDK, practicuscore.

1. Loading the "income" dataset

2. Profiling the dataset

3. Applying pre-process steps:
    - Suppressing outliers by using snippets
    - Applying one hot encoding
    - Applying label encoding
    - Re-naming columns
    - Deleting columns
    - Applying standardization by using snippets



### Step-1: Loading the Dataset

```python
dataset_conn ={
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/income.csv"
}
```

```python
import practicuscore as prt

region = prt.current_region()
worker = region.get_or_create_worker()
proc = worker.load(dataset_conn)

proc.show_head()
```

### Step-2: Profiling the dataset


"ydata_profiling" Python library is a powerful tool for data analysts and data scientists to analyze data sets quickly and effectively. 

The ProfileReport method of this library performs a thorough inspection of a data frame and generates a detailed profile report. This report provides comprehensive summaries of the dataset's overall statistics, missing values, distributions, correlations and other important information. With the report, users can quickly identify potential problems and patterns in the data set, which greatly speeds up and simplifies the data cleaning and pre-processing phases.

```python
from ydata_profiling import ProfileReport
```

```python
df_raw = proc.get_df_copy()
```

```python
ProfileReport(df_raw)
```

### Step-3: Pre-process


#### 3.1: Handling with missing values


The 'handle_missing' method of the SDK can be utilized to fill or drop missing values on target columns.

- technique: The method which used in handling missing value. It could take the values down below:
    - 'delete': drops the rows with missing values
    - 'custom': filling the missing values with a custom value
    - 'minimum': filling the missing values with minunmum value of column
    - 'maximum': filling the missing values with maximum value of column
    - 'average': filling the missing values with average value of column
- column_list: List of targeted columns (columns with missing values)
- custom_value: The value which will be used in filling columns, if not using 'custom' method leave it to be 'None'

```python
proc.handle_missing(technique='minimum', column_list=['workclass'], custom_value='None')
proc.handle_missing(technique='custom', column_list=['native-country'], custom_value='unknown')
```

#### 3.2: Suppressing of outliers by using snippets

Snippets are built-in python functions prepared by Practicus AI but, also you can build your own snippets for your company (for more information please visit https://docs.practicus.ai/tutorial)

To utilize snippets effectively, ensure that you create and open a folder named 'snippets' within your working directory. Then, place the snippet files into this designated folder.

Every snippets has parameters which are optional or mandatory to run. You can checkout the parameters within the snippet code.

E.g. the paramaters within 'suppress_outliers' can be listed as:
- outlier_float_col_list: list[str] | None (List of numeric columns to check for outliers. If left empty, applies to all numeric columns.),
- q1_percentile: float = 0.25 (Custom percentile for Q1, takes 0.25 as default value),
- q3_percentile: float = 0.75 (Custom percentile for Q3, takes 0.75 as default value),
- result_col_suffix: str | None = "no_outlier" (suffix for the new column where the suppressed data will be stored, takes "no_outlier" as default),
- result_col_prefix: str | None = None (Prefix for the new column where the suppressed data will be stored.),

```python
proc.run_snippet( 
    'suppress_outliers', 
    outlier_float_col_list=["capital-gain", "capital-loss"],
    q1_percentile = 0.05,
    q3_percentile = 0.95
)
```

#### 3.3: One-hot Encoding

The 'one_hot' method of the SDK can be utilized to apply one-hot encoding to the selected column.

- column_name: The name of the current column to be one-hot encoded.
- column_prefix: A prefix to use for the new one-hot encoded columns.

```python
cat_col_list = [
    'workclass', 
    'education', 
    'marital-status', 
    'occupation', 
    'relationship', 
    'native-country'
]
```

```python
for col in cat_col_list:
    proc.one_hot(column_name=col, column_prefix=col)
```

#### 3.4: Label Encoding

The 'categorical_map' method of the SDK can be utilized to apply label encoding to the selected column.

- column_name: The name of the current column to be one-hot encoded.
- column_prefix: A prefix to use for the new one-hot encoded columns.

```python
proc.categorical_map(column_name='sex', column_suffix='cat')
```

#### 3.5: Re-naming Columns

The 'rename_column' method of the SDK can be utilized to rename columns.

```python
proc.rename_column('hours-per-week', 'hours_per_week')
```

```python
proc.rename_column('capital-loss', 'capital_loss')
```

```python
proc.rename_column('capital-gain', 'capital_gain')
```

```python
proc.rename_column('education-num', 'education_num')
```

```python
proc.rename_column('income >50K', 'income_50K') 
```

#### 3.6: Deleting Columns

The 'delete_columns' method of the SDK can be utilized to delete columns.

```python
proc.delete_columns(['sex', 
                     'workclass', 
                     'education', 
                     'marital-status', 
                     'occupation', 
                     'relationship', 
                     'native-country'])
```

#### 3.7: Standardization of numerical columns

The 'normalize.py' snippet of the SDK can be utilized to apply standardization to numeric columns.

```python
proc.run_snippet( 
    'normalize', 
    numeric_col_list=['age', 'education_num', 'capital_gain', 'capital_loss', 'hours_per_week'],    
    normalization_option="Min-Max Normalization",  
    result=None
) 
```

#### 3.8: Logging the pre-process

The 'wait_until_done' and 'show_logs' methods of the SDK can be utilized to check and log the pre-process steps.


```python
proc.wait_until_done()
proc.show_logs()
```

#### 3.9: Exporting the data set into pandas dataframe

The 'get_df_copy' methods of the SDK can be utilized to export the dataset as pandas dataframe to continue working with dataset on diffrent aspect of Data Science.

```python
df_processed = proc.get_df_copy()
```

```python
df_processed.head()
```

```python
ProfileReport(df_processed)
```

```python
proc.kill()
```


## Supplementary Files

### snippets/impute_missing_knn.py
```python
from enum import Enum


class WeightsEnum(str, Enum):
    uniform = "uniform"
    distance = "distance"


def impute_missing_knn(df, missing_val_col: list[str] | None, n_neighbors: int = 5, weights: WeightsEnum = WeightsEnum.uniform):
    """
    Replaces each missing value using K-Nearest Neighbors technique
    :param missing_val_col: Columns to impute missing values. Leave empty for all columns
    :param n_neighbors: Number of neighboring samples to use for imputation.
    :param weights: Weight function used in prediction
    """
    import pandas as pd
    import numpy as np
    from sklearn.impute import KNNImputer

    knn_imp = KNNImputer(n_neighbors=n_neighbors, weights=str(weights))

    numeric_df = df.select_dtypes(include=[np.number])

    if missing_val_col:
        non_numeric_columns = set(missing_val_col) - set(numeric_df.columns)
        if non_numeric_columns:
            raise ValueError(f"Please only select numeric columns to impute, or do not select any columns. Non-numeric columns: {non_numeric_columns}")

        imputed_data = knn_imp.fit_transform(numeric_df[missing_val_col])
        imputed_df = pd.DataFrame(imputed_data, columns=missing_val_col, index=numeric_df.index)
    else:
        imputed_data = knn_imp.fit_transform(numeric_df)
        imputed_df = pd.DataFrame(imputed_data, columns=numeric_df.columns, index=numeric_df.index)

    df.update(imputed_df)
    return df


impute_missing_knn.worker_required = True
impute_missing_knn.supported_engines = ['pandas']

```

### snippets/normalize.py
```python
from enum import Enum


class NormalizationOptions(str, Enum):
    Z_SCORE = "Z-Score Normalization"
    MIN_MAX = "Min-Max Normalization"
    ROBUST = "Robust Normalization"


def normalize(df, numeric_col_list: list[str] | None = None, normalization_option: NormalizationOptions = NormalizationOptions.Z_SCORE, result: list[str] | None = None):
    """
    Normalizes certain columns in the DataFrame with the selected normalization method.
    
    :param numeric_col_list: Names of the numeric columns to normalize. If None, all numeric columns are considered.
    :param normalization_option: Specifies the method for normalization: Z-Score (standardizes data), Min-Max (scales data to a fixed range, typically [0, 1]), or Robust (reduces the impact of outliers).
    :param result: Column names to write normalization results. If None, the original column names appended with "_normalized" will be used.
    """
    import numpy as np
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    
    # If no specific columns provided, use all numeric columns
    if numeric_col_list is None:
        numeric_col_list = df.select_dtypes(include=[np.number]).columns.tolist()

    # Process according to the selected normalization method
    if normalization_option == NormalizationOptions.Z_SCORE:
        scaler = StandardScaler()
    elif normalization_option == NormalizationOptions.MIN_MAX:
        scaler = MinMaxScaler()
    elif normalization_option == NormalizationOptions.ROBUST:
        scaler = RobustScaler()
    else:
        raise ValueError("Unsupported normalization option selected.")
    
    # Normalize specified columns and assign results either to new columns or overwrite them
    for col in numeric_col_list:
        normalized_col_name = col + "_normalized" if result is None else result.pop(0) if result else f"{col}_normalized"
        df[normalized_col_name] = scaler.fit_transform(df[[col]])

    return df


normalize.worker_required = True
```

### snippets/suppress_outliers.py
```python
def suppress_outliers(
        df, outlier_float_col_list: list[str] | None, q1_percentile: float = 0.25, q3_percentile: float = 0.75,
        result_col_suffix: str | None = "no_outlier", result_col_prefix: str | None = None):
    """
    Suppresses outliers in specified numeric columns of the dataframe based on custom percentile values for Q1 and Q3.
    Adds new columns with the selected suffix or prefix. If no suffix or prefix is provided, overwrites the existing column.
    :param outlier_float_col_list: List of numeric columns to check for outliers. If left empty, applies to all numeric columns.
    :param q1_percentile: Custom percentile for Q1 (e.g., 0.25 for 25th percentile).
    :param q3_percentile: Custom percentile for Q3 (e.g., 0.75 for 75th percentile).
    :param result_col_suffix: Suffix for the new column where the suppressed data will be stored.
    :param result_col_prefix: Prefix for the new column where the suppressed data will be stored.
    """
    import numpy as np

    # If no specific columns provided, use all numeric columns
    if not outlier_float_col_list:
        outlier_float_col_list = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(outlier_float_col_list) == 0:
        raise ValueError("No numeric column provided or located.")

    # Process each specified column
    for col in outlier_float_col_list:
        q1 = df[col].quantile(q1_percentile)
        q3 = df[col].quantile(q3_percentile)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        if result_col_suffix:
            new_col_name = f'{col}_{result_col_suffix}'
        elif result_col_prefix:
            new_col_name = f'{result_col_prefix}_{col}'
        else:
            new_col_name = col

        # Create a new column (or override), with suppressed values
        df[new_col_name] = np.where(
            df[col] < lower_bound, lower_bound, np.where(df[col] > upper_bound, upper_bound, df[col])
        )
    
    return df

```


---

**Previous**: [Analyze](../../data-analysis/eda/analyze.md) | **Next**: [Process Data > Insurance](../process-data/insurance.md)
