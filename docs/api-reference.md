
## export_data

```Python
export_data(data_set, output_path, columns=None, reindex=False)
```

Exports a dataset to an Excel file (.xlsx) to be used with Microsoft Excel, Google Sheets, LibreOffice etc. 

**data_set**: Pandas DataFrame (recommended), NumPy Array or Python list. For large datasets, we recommend Pandas DataFrame.

**output_path**: The path where the Excel file will be written. If there is no file extension, Practicus AI will automatically add .xlsx to the file name.  

**columns**: Optional, default is *None*. We highly recommend providing column names if the data_set does not include them. If no column names are found, Practicus AI will automatically add names for you, such as column_1, column_2 etc. These names will not lead to the best user experience.   

**reindex**: Optional, default is *False*. If a Pandas DataFrame is used to export_data function, Practicus AI will use the index found in this data frame, or create one if none found. After several cycles of "exporting and applying changes", indexes might start jumping from value to value, such as 0, 5, 14 because of  filtering values. Although it is perfectly fine for Practicus AI to work with sparse index values like these, in some cases it can confuse end users. When reindex=True, Practicus AI will reset the index, so it will become like 0, 1, 2 again.

```python
# Example 1, exporting basic Python Array

# define a basic array
arr = [[1,2,3],
       [4,5,6],
       [7,8,9]]

import practicus

# write to Excel. Since no colum names are provided, practicus will create new names
practicus.export_data(arr, "basic_array.xlsx")

# Now, with column names
practicus.export_data(arr, "basic_array_2.xlsx", columns=['x1', 'x2', 'x3'])


# Example 2, exporting NumPy Array
from sklearn.datasets import load_boston

data_set = load_boston()
numpy_array = data_set.data

practicus.export_data(numpy_array, "boston_house_numpy.xlsx", 
                  columns=data_set.feature_names)


# Example 3, exporting Pandas Data Frame (recommended)
import pandas as pd
df = pd.DataFrame(data=data_set.data, columns=data_set.feature_names)

# no need to pass columns since the pandas data frame already has them 
practicus.export_data(df, "boston_house_pandas.xlsx")


# Example 4, reindexing 

# let's delete first 5 rows from the data frame 
df = df.drop(df.index[[0,1,2,3,4]])

# reindexing will start the index from 0 again
practicus.export_data(df, "boston_house_pandas_reindexed.xlsx", reindex=True)
```



## apply_changes

```Python
data_set2 = apply_changes(data_set, input_path, columns=None, inplace=False, reindex=False)
```

Applies detected or passed changes to the data_set. The way apply_changes() work depends on what kind of file is passed in input_path. If an Excel (.xlsx) file is passed, apply_changes() first executes detect_changes() to find out what kind of changes are made to the Excel (.xlsx) file, writes these changed to a .dp file and then applies these changes to the data_set. If input_path is a .dp file, detect_changes() is not called, and updates are applied directly from the .dp file.  

**data_set**: Pandas DataFrame, NumPy Array or Python list. For large datasets, Pandas DataFrame will perform faster.

**input_path**: This can be either an Excel (.xlsx) file with some changes in it, **or** a data prep (.dp) file that has changes recorded in it.   

**columns**: Optional, default is *None*. We highly recommend providing column names if the data_set does not include them. If no column names found, Practicus AI will automatically add names for you, such as column_1, column_2 etc.  Being consistent in column names between export_data() and apply_changes() is important since the column names in the Excel file and the data_set we later try to apply changes on should match. 

**inplace**: Optional, default is *False*. If inplace=True, Practicus AI will apply updates *directly* on the data_set provided as an input, and will *not* return anything back. Please note that inplace editing only works  if a Pandas DataFrame is provided as an input. inplace editing *might* have some performance benefits for very large datasets. We discourage using inplace updates unless it is necessary, since it becomes harder to retry code. I.e. if the applied changes do not work as you expect, you can open the auto-generated .dp file, make changes and can re-run apply_changes(). This will not work with inplace=True.

**reindex**: Optional, default is *False*. Only meaningful if a Pandas Data Frame is used. After several cycles of "exporting and applying changes", indexes might start jumping from value to value i.e. 0, 5, 14 due to filtering of values. Although it is perfectly fine for Practicus AI to work with sparse indexes, in some cases these kinds of indexing can confuse end users. When reindex=True, Practicus AI will reset the index so the *returned* data_set will have indexes reset, i.e. 0,1,2,3. 

**Returns**: The exact same type of data_set, with changes applied. If a Pandas DataFrame as passed as input value, this function return a Pandas DataFrame. Same for NumPy Array and Python Lists. If inplace=True, returns nothing.  Other than returning the data_set, apply_changes also writes a new .dp file with changes detected in it, if an Excel (.xlsx) file is passed in input_path. 

```python
# Example 1

arr = [[1,2,3],
       [4,5,6],
       [7,8,9]]

import practicus
practicus.export_data(arr, "basic_array_2.xlsx", columns=['x1', 'x2', 'x3'])

# now open the excel file and delete first column, x1
```

```python
# running the  below will detect the change we made (drop column), 
# apply it to arr and return a new Array  
arr2 = practicus.apply_changes(arr, "basic_array.xlsx", columns=['x1', 'x2', 'x3'])
# You should see something like the below  in output window.
```

```
Detecting changes made in basic_array.xlsx
Saved changes to data preparation file basic_array.dp in 0.21 seconds.

Applying changes from basic_array.dp
Input_Columns = [x1], [x2], [x3]
 Input columns match the DataFrame.

# Columns deleted in Excel 
Running: Drop_Column(Col[x1])
 Completed. 

All steps completed.
```

```python
# Example 2, inplace updates. (Pandas data frame is required for this to work)
import pandas as pd
df = pd.DataFrame(data=arr, columns=['x1', 'x2', 'x3'])

# with inpalce=True, apply_changes() doesn't return anything 
practicus.apply_changes(df, "basic_array.xlsx", inplace=True)
# confirm x1 column is dropped
display(df)

#Example 3, reindexing
# now open basic_array.xlsx and put a filter on x2, uncheck 2 and leave 5 and 8 only
# (to filter in Excel, you can click the drop down arrow next to the column name, x2)   
# reindexing will start the index from 0 again
df = pd.DataFrame(data=arr, columns=['x1', 'x2', 'x3'])
df2 = practicus.apply_changes(df, "basic_array.xlsx", reindex=True)
display(df2)
```



```
  x2  x3
0  5   6
1	 8   9
```



## detect_changes

```python
detect_changes(input_path, output_path=None)
```

This function detects changes a user makes inside the Excel (.xlsx) file and writes the detected changes to a data prep (.dp) file. Once the data prep (.**dp**) file is created, you can review and make changes as needed and then finally run using **apply_changes** function.     

**input_path**: Excel (.xlsx) file path with some changes in it. 

**output_path**: *Optional*. The path for the data prep (.dp) file that the detected changes will be written to. If no file name is passed, Practicus AI uses the same name of the input_path and replaces .xlsx with .dp. 

**Returns**: The path of the .dp file. If output_path is provided this function returns that name, if output_path was empty, returns the name of the filename that is generated.   

```python
# Example 1 

# the below code detects all changes made in the excel file, 
# and writes the result into basic_array.dp
practicus.detect_changes("basic_array.xlsx")

# open basic_array.dp file, you will see the below
```

```
Input_Columns = [x1], [x2], [x3]

# Columns deleted in Excel 
Drop_Column(Col[x1])

# Filtered rows in Excel 
Remove_Except(Col[x2] is in [5, 8])
```

```python
# let's assume we don't want to filter anymore. 
# Place a # in front of Remove_Except(..) to comment it out, and save the .dp file

# now let's apply changes to arr, but this time directly from .dp file
# instead of .xlsx file.
arr2 = practicus.apply_changes(arr, "basic_array.dp", columns=['x1', 'x2', 'x3'])

display(arr2)
# the result will be: [[2, 3], [5, 6], [8, 9]]
# first column (x1) dropped, but teh value 2 is "not" filtered out , 
# since we commented the filter line out with # in the .dp file 
```



## export_model

```python
export_model(model, output_path, columns="", target_name="", num_rows=1000)
```

Exports a model to an Excel (.xlsx) file, so that users can understand how the model works, and make predictions by entering new values. 

**model**: A Python model, pipeline, or the path of a .pmml file. If a model is passed, Practicus AI can read Linear Regression,  Logistic Regression, Decision Trees and Support Vector Machine models. If a pipeline is passed, Practicus AI can read several pre-processing steps like StandardScaler, MinMaxScaler etc, in addition to the model trained as part of the pipeline. Practicus AI can also read .pmml files, especially for models built outside of the Python environment like R, KNIME etc.   

**output_path**: The path of the Excel (.xlsx) file to export.

**columns:** *Optional, if a .pmml file is passed as model and has column names in it. Otherwise, required.* The column names that will be used as input features for the model. For a basic linear model,  y = 2 * x1 + 3 * x2,  'x1' and 'x2' are the input feature names. These names can be used as column names in the Excel file.

**target_name:** *Optional, if a .pmml file is passed as model and has column names in it. Otherwise, required.* The target column name that the model predicts for. For a basic linear model,  y = 2 * x1 + 3 * x2,  'y' would be the target name.

**num_rows:** *Optional, defaults to 1000 rows.* Indicates the number of rows to use in the Excel (.xlsx) file to make predictions on. Max 1,048,576 rows are supported, but the performance will depend on model's complexity, and the user's computer speed. Please gradually increase and test number of rows before sending the .xlsx file to others.     

**Returns**: The path of the .dp file. If output_path is provided this function returns that name, if output_path was empty, returns the name of the filename that is generated.   See some limitations below.

```python
# Example 1, model exporting
# ... model training code here ... 
some_model.fit(X, Y)

import practicus
practicus.export_model(some_model, output_path="some_model.xlsx",
                   columns=['X1', 'X2'], target_name="Some Target", num_rows=100)

# Example 2, pipeline exporting
# ... model and pipeline code here ...
my_pipeline = make_pipeline(
    SomePreProcessing(),
    SomeOtherPreProcessing(),  
    SomeModelTraining())

practicus.export_model(my_pipeline, output_path="some_model.xlsx",
                   columns=['Column 1', 'Column 2'], target_name="Target", num_rows=150)


# Example 3, pmml model exporting

# let's assume we have a model trained in R, and saved in a .pmml file
# let's also assume the .pmml file has column and target names in it
practicus.export_model("some_R_model.pmml", output_path="some_R_model.xlsx", num_rows=150)

# Please check the Samples section for more.. 
```

### export_model limitations

Practicus AI is new and we are looking forward to hearing your feedback on adding new features. some of our current limitations are: 

- Exported models need to have fewer than 16,384 columns.  

- Maximum 1 million rows (1,048,576) are supported for both data preparation and model exporting. 

- Model exporting currently work with Linear Regression, Logistic Regression, Decision Trees and Support Vector Machines. According to Kaggle forums, Google search trends and other forums, these are by far the most popular modeling techniques potentially covering 90+% of the predictive ML analytics use cases. Practicus AI currently doesn't target model exporting for cognitive use cases and deep learning frameworks, since the resulting Excel file would become very complicated making  model debugging and model explainability challenging.

  