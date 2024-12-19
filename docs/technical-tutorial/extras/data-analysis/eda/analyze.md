---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# EDA Sample


## Example: End-to-End Exploratory Data Analysis (EDA)

In this example, we will perform a complete EDA process, covering the following topics:

- **Column Separation**: 
  - We will separate the columns in the dataset according to their types.
  
- **Column Exploration**: 
  - Explore the separated columns to understand their characteristics.
  
- **Outlier Detection and Handling**: 
  - Identify outliers using thresholds and replace them with suitable values.
  
- **Correlation Analysis**: 
  - Analyze the correlation between numerical features to uncover relationships.


```python
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.style as plt_styl

import warnings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 30)
pd.set_option('display.width', 150)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
warnings.simplefilter(action = "ignore")
```

Get connection for dataset

```python
data_set_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/insurance.csv"
}
```

Create worker and start process

```python
import practicuscore as prt

worker = prt.get_local_worker()

proc = worker.load(data_set_conn, engine='AUTO') 

df = proc.get_df_copy()
display(df)
```

```python
df.info()
```

Separate columns according to column types



### **Objective**
The `grab_col_names` function aims to identify and classify columns in a given DataFrame into different types based on their data characteristics.

### **Functionality**
- **Date Columns (`date_cols`)**:
  - Identifies columns with a `datetime64[ns]` data type.
- **Categorical Columns (`cat_cols`)**:
  - Includes columns of type `object` or `category`.
  - Includes numeric columns with a number of unique values below the `cat_th` threshold (default is 10), classifying them as categorical.
- **Numerical Columns (`num_cols`)**:
  - Columns with `float` or `integer` types that are not classified as `num_but_cat`.
- **Categorical but Cardinal Columns (`cat_but_car`)**:
  - Categorical columns with unique values exceeding the `car_th` threshold (default is 25).
- **Numerical but Categorical Columns (`num_but_cat`)**:
  - Numeric columns with fewer unique values than the `cat_th` threshold, treating them as categorical.


```python
def grab_col_names(dataframe, cat_th=10, car_th=25, show_date=False):
    date_cols = [col for col in dataframe.columns if dataframe[col].dtypes == "datetime64[ns]"]
    cat_cols = dataframe.select_dtypes(["object", "category"]).columns.tolist()
    num_but_cat = [col for col in dataframe.select_dtypes(["float", "integer"]).columns if dataframe[col].nunique() < cat_th]
    cat_but_car = [col for col in dataframe.select_dtypes(["object", "category"]).columns if dataframe[col].nunique() > car_th]
    cat_cols = cat_cols + num_but_cat
    cat_cols = [col for col in cat_cols if col not in cat_but_car]
    num_cols = dataframe.select_dtypes(["float", "integer"]).columns
    num_cols = [col for col in num_cols if col not in num_but_cat]

    print(f"Observations: {dataframe.shape[0]}")
    print(f"Variables: {dataframe.shape[1]}")
    print(f'date_cols: {len(date_cols)}')
    print(f'cat_cols: {len(cat_cols)}')
    print(f'num_cols: {len(num_cols)}')
    print(f'cat_but_car: {len(cat_but_car)}')
    print(f'num_but_cat: {len(num_but_cat)}')


    if show_date == True:
        return date_cols, cat_cols, cat_but_car, num_cols, num_but_cat
    else:
        return cat_cols, cat_but_car, num_cols, num_but_cat
```

```python
cat_cols, cat_but_car, num_cols, num_but_cat = grab_col_names(df)
```

```python
print(cat_cols)
```

## Target Variable None (`target=None`)

For a categorical column:
- **COUNT**: The number of times each category occurs.
- **RATIO**: The percentage of the total data.
- Displays these as a table.

---

## If Target Variable Exists (`target!=None`)

In addition to the above, it shows the relationship between the target variable and the categorical variable:
- **TARGET_COUNT**: The total number of the target variable in the categorical variable.
- **TARGET_MEAN**: The average of the target variable for each category.
- **TARGET_MEDIAN**: The median of the target variable for each category.
- **TARGET_STD**: The standard deviation of the target variable for each category.


```python
def cat_analyzer(dataframe, variable, target = None):
    print(variable)
    if target == None:
        print(pd.DataFrame({
            "COUNT": dataframe[variable].value_counts(),
            "RATIO": dataframe[variable].value_counts() / len(dataframe)}), end="\n\n\n")
    else:
        temp = dataframe[dataframe[target].isnull() == False]
        print(pd.DataFrame({
            "COUNT":dataframe[variable].value_counts(),
            "RATIO":dataframe[variable].value_counts() / len(dataframe),
            "TARGET_COUNT":dataframe.groupby(variable)[target].count(),
            "TARGET_MEAN":temp.groupby(variable)[target].mean(),
            "TARGET_MEDIAN":temp.groupby(variable)[target].median(),
            "TARGET_STD":temp.groupby(variable)[target].std()}), end="\n\n\n")
```

```python
cat_analyzer(df, 'region') 
```

```python
df[num_cols].hist(figsize = (25,20), bins=15);
```

```python
df[num_cols].describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.95, 0.99]).T.drop(['count'], axis=1)
```

## Purpose of the Given Functions

### 1. **`outliers_threshold`**
- **Purpose**: Calculates the threshold values for detecting outliers in a numerical column.
- **How it Works**:
  - Uses the interquartile range (IQR) method based on the 5th and 95th percentiles.
  - Defines outliers as values below `Q1 - 1.5 * IQR` or above `Q3 + 1.5 * IQR`.

---

### 2. **`grab_outlier`**
- **Purpose**: Identifies outliers in a specified column and optionally returns their indices.
- **How it Works**:
  - Detects outliers using the thresholds calculated by `outliers_threshold`.
  - Prints the rows containing outliers. 
  - If the `index` parameter is set to `True`, it returns the indices of the outliers.

---

### 3. **`replace_with_thresholds`**
- **Purpose**: Replaces outliers in a numerical column with the calculated threshold values.
- **How it Works**:
  - Detects outliers using `outliers_threshold`.
  - If an outlier is below the lower threshold, it is replaced with the lower threshold value.
  - If an outlier is above the upper threshold, it is replaced with the upper threshold value.


```python
# This function calculates the threshold values to be used to detect outliers of a column.
def outliers_threshold(dataframe, column):
    q1 = dataframe[column].quantile(0.05)
    q3 = dataframe[column].quantile(0.95)
    inter_quartile_range = q3 - q1
    low = q1 - 1.5 * inter_quartile_range
    up = q3 + 1.5 * inter_quartile_range
    return low, up

# This function detects outliers in a column and optionally returns their index.
def grab_outlier(dataframe, column, index=False):
    low, up = outliers_threshold(dataframe, column)
    if dataframe[(dataframe[column] < low) |
                 (dataframe[column] > up)].shape[0] < 10:
        print(dataframe[(dataframe[column] < low) | (dataframe[column] > up)][[column]])
    else:
        print(dataframe[(dataframe[column] < low) |
                 (dataframe[column] > up)][[column]])
    if index:
        outlier_index = dataframe[(dataframe[column] < low) |
                                  (dataframe[column] > up)].index.tolist()
        return outlier_index
# This function replaces outliers with threshold values.
def replace_with_thresholds(dataframe, col_name):
    low_limit, up_limit = outliers_threshold(dataframe, col_name)
    if low_limit > 0:
        dataframe.loc[(dataframe[col_name] < low_limit), col_name] = low_limit
        dataframe.loc[(dataframe[col_name] > up_limit), col_name] = up_limit
    else:
        dataframe.loc[(dataframe[col_name] > up_limit), col_name] = up_limit
```

```python
df[df['age'] <= 64]['age'].plot(kind='box')
```

Perform the outlier operation

```python
for col in num_cols:
        print('********************************************************************* {} *****************************************************************************'.format(col.upper()))
        grab_outlier(df, col, True)
        replace_with_thresholds(df, col)
        print('****************************************************************************************************************************************************************', end='\n\n\n\n\n')
```

This code snippet visualizes the correlations between numerical columns in a dataset using a heatmap. Correlation measures the statistical relationship between two variables. The heatmap provides a visual representation, showing how strongly each column is related to others.

```python
import matplotlib.pyplot as plt
```

```python
plt.figure(figsize=(30,20))
corr_matrix = df.select_dtypes(include=['int64', 'int32', 'float64']).corr()
sns.heatmap(corr_matrix, annot=True, cmap='Reds')
plt.title('Correlation Heatmap')

```

## Summarizing a Categorical Column

### 1. Frequency and Ratio Table
For each category in the column:
- **Frequency (Count)**: The number of times each category is repeated.
- **Percentage (Ratio)**: The proportion of the category in the total data.
- Displays these metrics in a table format.

---

### 2. Plotting (Optional)
If the argument `plot=True` is provided:
- Visualizes the frequencies of the categories in the column using a **bar chart**.
- Each bar is labeled with the percentage of the category in the total dataset.


```python
def cat_summary(dataframe, x_col, plot=False, rotation=45):
    display(pd.DataFrame({x_col: dataframe[x_col].value_counts(),
                          "Ratio": 100 * dataframe[x_col].value_counts() / len(dataframe)}))

    if plot:
        count = dataframe.groupby(x_col).size().sum()
        dataframe_grouped = dataframe.groupby(x_col).size().reset_index(name='counts').sort_values('counts', ascending=False)
        num_bars = len(dataframe_grouped[x_col].unique())
        colors = plt.cm.Set3(np.linspace(0, 1, num_bars))
        fig, ax = plt.subplots(figsize=(8, 5))

        x_pos = range(len(dataframe_grouped[x_col]))

        ax.bar(x_pos, dataframe_grouped['counts'], color=colors)
        ax.set_xlabel(x_col)
        ax.set_ylabel('Count')
        ax.set_title(f'Distribution by {x_col}')

        ax.set_xticks(x_pos)
        ax.set_xticklabels(dataframe_grouped[x_col], rotation=rotation)

        for i, value in enumerate(dataframe_grouped['counts']):
            ax.annotate('{:.1%}'.format(value / count), (i, value), textcoords="offset points", xytext=(0, 10), ha='center')

        plt.show()

```

```python
for col in cat_cols:
    cat_summary(df, col, plot=True)
```

Kill proc when your process is finished.

```python
proc.kill()
```


---

**Previous**: [Multiple Layers](../plot/multiple-layers.md) | **Next**: [Data Processing > Pre Process Data > Preprocess](../../data-processing/pre-process-data/preprocess.md)
