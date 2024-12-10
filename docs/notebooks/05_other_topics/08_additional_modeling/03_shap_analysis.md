---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus AutoML
    language: python
    name: practicus_ml
---

```python
import numpy as np
import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import shap
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.tree import plot_tree
```

```python
# load the csv file as a data frame
df = pd.read_csv('samples/iris.csv')
```

```python
label_encoder = LabelEncoder()
df['species'] = label_encoder.fit_transform(df['species'])
```

```python
# Separate Features and Target Variables
X = df.drop(columns='species')
y = df['species']
```

```python
# Create Train & Test Data
X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.3,
                                                	stratify =y,
                                                	random_state = 13)

# Build the model
rf_clf = RandomForestClassifier(max_features=2, n_estimators =100 ,bootstrap = True)

rf_clf.fit(X_train, y_train)
```

```python
y_pred = rf_clf.predict(X_test)
print(classification_report(y_pred, y_test))
```

# Iris Data Set Feature Importance

## Overview
The following visualization presents a ranked bar chart depicting the relative importance of each feature used by our machine learning model to predict Iris flower species. In this analysis, we observe the features derived from the dimensions of the flower's petals and sepals: `petal_width`, `petal_length`, `sepal_length`, and `sepal_width`.

## Interpretation
- **Petal Width (petal_width):** This feature has the highest relative importance score, indicating its strong predictive power in distinguishing between Iris species. The model heavily relies on petal width, suggesting that this attribute significantly influences the model's decision-making process.
- **Petal Length (petal_length):** Following petal width, petal length also shows substantial influence on the model's predictions. Its prominence implies that the length of the petal is another defining characteristic in species classification.
- **Sepal Length (sepal_length) & Sepal Width (sepal_width):** These features hold less significance compared to petal measurements. Their lower importance scores may reflect their reduced discriminative ability in the context of this specific model and dataset.

## Implications for Model Refinement
We leverage this feature importance chart to guide feature selection and model simplification efforts. In high-dimensional datasets, reducing model complexity and computational load by pruning less significant features is crucial. Additionally, the chart enhances model interpretability by highlighting which features predominantly drive predictions, providing insights into potential dependencies within the dataset.

For instance, if petal measurements are more influential than sepal measurements, it could indicate that petals play a more decisive role in identifying the Iris species. 

## Conclusion
This graphical analysis is instrumental for data-driven decision-making, ensuring that our model is both efficient and interpretable. By focusing on the most informative features, we can streamline the model while maintaining or even enhancing its accuracy.


```python
importances = rf_clf.feature_importances_
indices = np.argsort(importances)
features = df.columns
plt.title('Feature Importances')
plt.barh(range(len(indices)), importances[indices], color='y', align='center')
plt.yticks(range(len(indices)), [features[i] for i in indices])
plt.xlabel('Relative Importance')
plt.show()
```

```python
# compute SHAP values
explainer = shap.TreeExplainer(rf_clf)
shap_values = explainer.shap_values(X)

class_names = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
```

<!-- #region -->
# Random Forest Component Analysis: Decision Tree Visualization

## Overview
This visualization illustrates a single decision tree from a Random Forest classifier trained on the Iris dataset. It's a visual representation of how the algorithm makes decisions and classifies different Iris species: setosa, versicolor, and virginica.


## Specific Observations
- The first split is made with the condition `petal_width <= 0.75`, perfectly separating Iris setosa from the other species with a Gini score of 0.0 and 25 samples at the node.
- Subsequent splits focus on distinguishing Iris versicolor and Iris virginica, proceeding until reaching nodes with lower Gini scores.

## Importance for Model Interpretation
- Such visualizations are crucial for understanding the decision-making process of the model and determining which features are most influential during the classification task.
- The explainable nature of decision trees allows us to clearly communicate how the model works and when specific features become significant, enhancing the transparency and reliability of the AI model.

## Implications for Stakeholders
- The clear delineation of decision paths provides stakeholders with insight into the model's reasoning, facilitating trust in the predictions made by the AI system.
- It underscores the model's dependence on petal measurements, potentially informing feature engineering and data collection priorities for future modeling efforts.

## Conclusion
This decision tree is a testament to the power of Random Forest in handling complex classification tasks. By breaking down the decision process step by step, we gain a granular understanding of feature importance and model behavior, laying a foundation for informed model refinement and application.

<!-- #endregion -->

```python
from sklearn.tree import plot_tree


feature_names = list(X_train.columns)

# Select one of the trees from your random forest
tree_to_plot = rf_clf.estimators_[0]

# Plot the selected tree
fig = plt.figure(figsize=(25,20))
_ = plot_tree(tree_to_plot,
              feature_names=feature_names,
              class_names=class_names,
              filled=True)
```

# SHAP Value Summary: Feature Importance for Iris Classification

## Overview
This graph utilizes SHAP (SHapley Additive exPlanations) values to provide a summary of feature importance within our Iris species classification model. The length of the bars represents the average impact of each feature on the model's predictions, across all instances in the dataset.

## Detailed Feature Contributions
- **Petal Width (petal_width):** Stands out as the feature with the most significant positive impact on model output, particularly for Iris-virginica predictions. The prominence of this bar suggests that petal width is a critical factor in the classification.
- **Petal Length (petal_length):** Exhibits a notable positive influence as well, especially for Iris-setosa. Its impact underlines the importance of petal length in distinguishing this particular species.
- **Sepal Measurements (sepal_length and sepal_width):** While having a lesser effect compared to petal features, these still contribute to the model's decision-making process, with sepal_length showing some influence on Iris-versicolor classification.

## Model Insight and Adjustments
- This visualization is a powerful tool for identifying potential biases or over-reliance on specific features. The predominance of petal-related features may suggest the need for balance through feature engineering or model hyperparameter tuning.
- The insight provided by this summary plot is critical for enhancing model fairness, balance, and ultimately, the trustworthiness of its predictions.

## Conclusion
The SHAP summary plot offers an in-depth understanding of how each feature influences the classification model. It is essential for developers and stakeholders to make data-driven decisions regarding feature selection and to grasp the relative importance of attributes within the dataset.


```python
shap.summary_plot(shap_values, X.values, plot_type="bar", class_names= class_names, feature_names = X.columns)
```

# SHAP Summary Plot for Iris Dataset Model Interpretation

## Overview
This SHAP (SHapley Additive exPlanations) summary plot provides a visual representation of the feature impact within our classification model for the Iris dataset. It quantifies the marginal contribution of each feature to the prediction made by the model, offering insights into the decision-making process.

## Interpretation of SHAP Values
- **Positive and Negative Impacts:** The distribution of SHAP values on the x-axis reveals how each feature affects the model output for individual observations. Red points indicate higher feature values, while blue points represent lower values, demonstrating the directional impact of features on the model output.
- **Feature Contributions:** For instance, `petal_width` is shown to have a predominantly positive impact on the model's predictions—most red points lie to the right of the zero line, suggesting that higher petal width values tend to increase the likelihood of a particular Iris species prediction.

## Data Point Analysis
- Each point on the graph corresponds to a unique observation in the dataset. The spread of these points allows us to discern how the model differentiates between the samples, particularly noting the variability of effects across the range of feature values.

## Utility of SHAP Summary
- **Model Interaction:** The SHAP values elucidate interactions between features and their directional influence on predictions, offering a reliable method to transparently showcase how feature variations influence the model's decisions.
- **Insights for Model Improvement:** This analysis is instrumental in enhancing our understanding of the model and explaining the heterogeneity and complexity present in the predictions. It aids in identifying areas for model improvement, guiding feature engineering, and ensuring robust prediction performance.

## Conclusion
By employing the SHAP summary plot, we provide a granular view of feature influences, enhancing interpretability and trust in our model. It serves as a valuable tool for stakeholders alike, enabling data-driven decision-making and promoting a thorough comprehension of the model's predictive dynamics.


```python
shap.summary_plot(shap_values[1], X.values, feature_names = X.columns)

```

```python
shap.summary_plot(shap_values[0], X.values, feature_names = X.columns)

```

```python
shap.summary_plot(shap_values[2], X.values, feature_names = X.columns)

```

# SHAP Dependence Plot: Sepal Length's Influence on Iris Classification

## Overview
This SHAP dependence plot showcases the relationship between `sepal_length` and the model output, while also highlighting the impact of another feature, `sepal_width`, using a color gradient. We analyze how variations in sepal dimensions influence the classification predictions made by the model.

## Key Observations
- **Sepal Length Impact:** As `sepal_length` increases, we observe a general trend of decreasing SHAP values, indicating a potentially negative influence on the model's confidence in predicting a particular Iris species.
- **Interaction Effect:** The color coding represents the `sepal_width` values, with warmer colors (red) indicating larger sepal widths. Notably, data points with larger `sepal_width` often correspond to higher SHAP values, suggesting that a wider sepal might counteract the negative impact of longer sepal length.

## Insights for Feature Interaction
- This plot allows us to discern not only the individual effects of features but also how they might interact with each other. For instance, while longer sepals (`sepal_length`) tend to decrease prediction confidence, this effect might be moderated by the width of the sepals (`sepal_width`).
- The variability in SHAP values across different `sepal_length` measurements, especially when colored by `sepal_width`, provides an understanding of how feature combinations affect model predictions.

## Implications for Model Refinement
- Such insights are valuable for stakeholders when considering how to optimize features and adjust the model. 
- Recognizing the influence of feature interactions is crucial for developing more robust and accurate classification models and can lead to more nuanced data preprocessing and feature engineering strategies.

## Conclusion
The dependence plot is a vital interpretability tool, allowing stakeholders to grasp the complex dynamics of feature interactions within the model. This understanding is imperative for fine-tuning the model to enhance predictive performance and ensure that it generalizes well to new data.



```python
shap.dependence_plot(0, shap_values[0], X.values, feature_names=X.columns)
```

```python
shap.dependence_plot(1, shap_values[0], X.values, feature_names=X.columns)
```

```python
shap.dependence_plot(2, shap_values[0], X.values, feature_names=X.columns)
```

<!-- #region -->
# SHAP Waterfall Plot Analysis for Individual Prediction

## Overview
The displayed SHAP waterfall plot is an interpretative tool used to break down the contribution of each feature to a specific prediction made by our machine learning model. It details the individual and cumulative impact of features on a single prediction.

## Feature Contributions Explained
- **Petal Measurements (petal_width and petal_length):** These features exhibit a strong positive effect on the model's output. 
- **Sepal Measurements (sepal_length and sepal_width):** While `sepal_length` shows a small positive contribution, `sepal_width` has a slight negative influence. The limited impact of `sepal_width` in this instance may suggest it plays a lesser role in the classification for this specific prediction.

## Addressing Feature Impact
- The substantial influence of petal measurements raises concerns about the model's reliance on a narrow set of features, which could lead to overfitting. This phenomenon occurs when a model learns patterns specific to the training data, impacting its ability to generalize to unseen data.
- To mitigate over-reliance and enhance generalization, regularization techniques may be employed, or the model could be adjusted to give more weight to other features in the dataset.


## Conclusion
Understanding which features the model prioritizes and the potential outcomes of this prioritization is central to data scientists' efforts to enhance the model's reliability and applicability. These analyses are crucial for maintaining a balanced performance of the model, ensuring that it remains robust across different scenarios.

<!-- #endregion -->

```python
row = 8
shap.waterfall_plot(shap.Explanation(values=shap_values[0][row], 
                                        base_values=explainer.expected_value[0], data=X_test.iloc[row],  
                                        feature_names=X_test.columns.tolist()))
```

```python
row = 42
shap.waterfall_plot(shap.Explanation(values=shap_values[0][row], 
                                        base_values=explainer.expected_value[0], data=X_test.iloc[row],  
                                        feature_names=X_test.columns.tolist()))
```

### SHAP Force Plot 

##### This SHAP Force Plot  illustrates the impact of each feature on our model's classification prediction. The "base value" represents our average reference prediction, while the "f(x) = 1.00" value is the definitive prediction made by our model for this instance. Red bars (petal length: 4.5, petal width: 1.3, and sepal length: 5.7) indicate factors that increase the model's prediction. These three features have elevated the prediction, with petal length having the most significant impact. Sepal width (2.8) presents a slight negative effect, causing a minimal decrease in the model's prediction. Overall, in light of these values, our model robustly classifies the given data point into a specific category.

```python
shap.plots.force(explainer.expected_value[0], shap_values[0][0,:], X_test.iloc[0, :], matplotlib = True)

```

### SHAP Decision Plot

##### The SHAP decision plot visualizes the impact of individual features on the output of a machine learning model. This particular plot is generated using the shap.decision_plot function with parameters corresponding to the expected value of the model, SHAP values for a set of predictions, and feature names from the test dataset:

X-axis: The model output value after accounting for the impact of each feature.
Lines: Represent the shift in the model output due to the impact of the corresponding feature from the base value.
Petal length: Shows a consistently negative impact on the model output.
Petal width: Generally contributes towards an increase in the model output.
Sepal length and sepal width: Exhibit variable impacts on the model output.
This plot is instrumental in pinpointing the most influential features for a prediction and understanding their collective impact on the final model output.

```python
#For class 0
shap.decision_plot(explainer.expected_value[0], shap_values[0], X_test.columns)
```

```python
# For class 1
shap.decision_plot(explainer.expected_value[1], shap_values[1], X_test.columns)
```

```python
# For class 2
shap.decision_plot(explainer.expected_value[2], shap_values[2], X_test.columns)
```


## Supplementary Files

### bank_marketing/snippets/label_encoder.py
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

### bank_marketing/snippets/one_hot.py
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

### model_tracking/model_drifts/model.py
```python
import os
from typing import Optional
import pandas as pd
from starlette.exceptions import HTTPException
import joblib 


model_pipeline = None


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, 'model.pkl')
    if not os.path.exists(model_file):
        raise HTTPException(status_code=404, detail=f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, df: Optional[pd.DataFrame] = None, *args, **kwargs) -> pd.DataFrame:
    if df is None:
        raise HTTPException(status_code=500, detail="No dataframe received")

    if 'charges' in df.columns:
        # Dropping 'charges' since it is the target
        df = df.drop('charges', axis=1)  

    # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['Predictions'])
    
    return predictions_df

```

### sparkml/model.json
```json
{
    "download_files_from": "cache/ice_cream_sparkml_model/",
    "_comment": "you can also define download_files_to otherwise, /var/practicus/cache is used"
}
```

### sparkml/model.py
```python
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
from pyspark.sql.types import StructType, StructField, DoubleType
from pyspark.ml.regression import LinearRegressionModel

spark = None
model = None

# Make sure you downloaded the SparkML model files to the correct cache folder
MODEL_PATH = "/var/practicus/cache/ice_cream_sparkml_model"


async def init(*args, **kwargs):
    global spark, model
    if spark is None:
        spark = SparkSession.builder.appName("IceCreamRevenuePrediction").getOrCreate()
    if model is None:
        model = LinearRegressionModel.load(MODEL_PATH)


async def predict(df: pd.DataFrame | None = None, *args, **kwargs) -> pd.DataFrame:
    # Define schema for Spark DataFrame
    schema = StructType([
        StructField("features", DoubleType(), True)
    ])
    
    # Convert input Pandas DataFrame to Spark DataFrame
    spark_data = spark.createDataFrame(
        df.apply(lambda row: (Vectors.dense(float(row['Temperature'])),), axis=1),
        schema=["features"]
    )
    
    # Make predictions using the Spark model
    predictions = model.transform(spark_data)
    
    # Select the relevant columns and convert to Pandas DataFrame
    predictions_pd = predictions.select("features", "prediction").toPandas()
    
    # Extract the Temperature and predicted Revenue for readability
    predictions_pd["Temperature"] = predictions_pd["features"].apply(lambda x: x[0])
    predictions_pd = predictions_pd.rename(columns={"prediction": "predicted_Revenue"})
    predictions_pd = predictions_pd[["predicted_Revenue"]]
    
    return predictions_pd

```

### streamlined_model_deployment/model.py
```python
import os
from typing import Optional
import pandas as pd
import numpy as np
from starlette.exceptions import HTTPException
import joblib
 
model_pipeline = None
 
def add_features(df):
    for column in df.select_dtypes(include='object'):
        mode_value = df[column].mode()[0]
        df[column] = df[column].fillna(mode_value)

    for column in df.select_dtypes(include='int64'):
        mean_value = df[column].mean()
        df[column] = df[column].fillna(mean_value)

    for column in df.select_dtypes(include='float64'):
        mean_value = df[column].mean()
        df[column] = df[column].fillna(mean_value)
    return df
 
async def init(model_meta=None, *args, **kwargs):
    global model_pipeline
 
    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, 'model.pkl')
    if not os.path.exists(model_file):
        raise HTTPException(status_code=404, detail=f"Could not locate model file: {model_file}")
 
    model_pipeline = joblib.load(model_file)
   
 
async def predict(http_request, df: Optional[pd.DataFrame] = None, *args, **kwargs) -> pd.DataFrame:
    if df is None:
        raise HTTPException(status_code=500, detail="No dataframe received")

    # Making predictions
    predictions = model_pipeline.predict(df)
 
    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['income >50K'])
 
    return predictions_df
```

### xgboost/model.py
```python
import os
import pandas as pd
import joblib

model_pipeline = None


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, 'model.pkl')
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, df: pd.DataFrame | None = None, *args, **kwargs) -> pd.DataFrame:
    if df is None:
        raise ValueError("No dataframe received")

    if 'charges' in df.columns:
        # Dropping 'charges' since it is the target
        df = df.drop('charges', axis=1)

        # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['Predictions'])

    return predictions_df

```

### xgboost/model_custom_df.py
```python
import os
import pandas as pd
import joblib

model_pipeline = None


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, 'model.pkl')
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, *args, **kwargs) -> pd.DataFrame:
    # Add the code that creates a dataframe using Starlette Request object http_request
    # E.g. read bytes using http_request.stream(), decode and pass to Pandas.
    raise NotImplemented("DataFrame generation code not implemented")

    if 'charges' in df.columns:
        # Dropping 'charges' since it is the target
        df = df.drop('charges', axis=1)

    # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['Predictions'])

    return predictions_df

```


---

**Previous**: [Deploy Model](02_deploy_model.md) | **Next**: [SparkML Ice Cream](sparkml/sparkml_ice_cream.md)
