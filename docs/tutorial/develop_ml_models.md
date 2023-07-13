# Develop Machine Learning Models with Jupyter Notebooks

_This section requires a Practicus AI Cloud Worker. Please visit the [introduction to Cloud Workers](worker-node-intro.md) section of this tutorial to learn more._

This section will provide information on how technical and non-technical users can easily intervene in the code and improve the machine learning models they build.

You have set up the model and everything is fine. You can either complete the model at this point and save it, or you can easily intervene in the generated Jupyter Notebook code to improve the model. 

- Open _Explore_ tab 
- Make sure a _Cloud Worker_ is selected (upper right)
- Select _Cloud Worker Files_ and open the file below 
- Home > samples > titanic.csv
- Select Model > Predictive Objective 
- Choose _Objective Column_ as Survived and _Technique_ should be Classifications
- Click _OK_
- After the model build is completed you will see a dialog
- Select _Open Jupyter Notebook to experiment further_

## Scale and Transform

In the _Scale and Transform_ section, you can rescale the values of numeric columns in the dataset without distorting differences in the ranges of values or losing information.

![scale_and_transform.png](img%2Fimprove_ml_models%2Fscale_and_transform.png)

Parameters for _Normalization_ in shortly:

 - You must first set normalize to True
 - You can choose z-score, minmax, maxabs, or robust methods for normalize

Parameters for _Feature Transform_ in shortly: 

 - You must first set normalize to True
 - You can choose _yeo-johnson_ or _quantile_ methods.
 - For the Target Transform you can choose _yeo-johnson_ or _quantile_ methods

![scale_and_transform_final.png](img%2Fimprove_ml_models%2Fscale_and_transform_final.png)

If you want to have deeper knowledge for _Scale and Transform_, you can review the following link

[If you want to have deeper knowledge for _Scale and Transform_, you can review this link](https://pycaret.gitbook.io/docs/get-started/preprocessing/scale-and-transform)

## Feature Engineering

In the _Feature Engineering_ section, you can automatically try new variables and have them improve the accuracy of the model. You can also apply rare encoding to data with low frequency

![feature_engineering.png](img%2Fimprove_ml_models%2Ffeature_engineering.png)

Parameters for _Polynomial Features_ in shortly:

 - You must first set _polynomial_features_ to True
 - polynomial_degree should be int

Parameters for _Bin Numeric Features_ in shortly:

 - _bin_numeric_features_ should be list

Parameters for _Combine Rare Levels_ in shortly:

 - rare_to_value: float, default=None
 - rare_value: default='rare'

![feature_engineering_final.png](img%2Fimprove_ml_models%2Ffeature_engineering_final.png)

If you want to have deeper knowledge for _Feature Engineering_, you can review the following link

[If you want to have deeper knowledge for _Feature Engineering_, you can review this link](https://pycaret.gitbook.io/docs/get-started/preprocessing/feature-engineering)

## Feature Selection

In the _Feature Selection_ section, you can set which variables to include in the model and exclude some variables based on the relationships between the variables.

![feature_selection.png](img%2Fimprove_ml_models%2Ffeature_selection.png)

Parameters for _Remove Multicollinearity_ in shortly:

 - You must first set _remove_multicollinearity_ to True
 - _multicollinearity_threshold_ should be float

Parameters for _Principal Component Analysis_ in shortly:

 - You must first set _pca_ to True
 - _pca_method_ should be _linear_, _kernel_, or _incremental_
 - _pca_components_ should be _None_, _int_, _float_, _mle_
 - Hint: Minka’s MLE is used to guess the dimension (ony for pca_method='linear')

Parameters for _Ignore Low Variance_ in shortly:

 - _low_variance_threshold_ should be float or None.


[If you want to have deeper knowledge for _Feature Selection_, you can review this link](https://pycaret.gitbook.io/docs/get-started/preprocessing/feature-selection)


[< Previous](chatgpt.md) | [Next >](next-steps.md)