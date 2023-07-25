Welcome to Practicus AI Model API documentation. You can use the [Practicus AI App](https://practicus.ai) or the SDK to build, distribute and deploy AI/ML models and then consume these models with the app or any other REST API compatible system.

### Model prefix concept

Practicus AI models are **logically** grouped with the model prefix concept using the https:// [some.address.com] / [some/model/prefix] / [model-name] format. E.g. https://practicus.company.com/models/marketing/churn can be a model API address where _models/marketing_ is the prefix and _churn_ is the model.

### Model Documentation

Models under a prefix can be viewed by using Practicus AI App. If your admin enabled them, you can also view the documentation by visiting _../prefix/redoc_ or _../prefix/docs_ or E.g. https://practicus.company.com/models/marketing/redoc

### Model Deployment concept

Models are **physically** deployed to Kubernetes deployment(s). These have several characteristics including capacity, auto-scaling, additional security etc.

### Authentication

Consuming models inside the Practicus AI app does not require additional authentication. For external use, you will need an access token. An admin can create tokens at the model prefix or individual model level.

### Submitting data in batches

Practicus AI app will automatically split large data into mini-batches to improve performance and avoid memory issues.  You are encouraged to do the same and submit data in a volume compatible with your model deployment capacity. E.g. If your model deployment pods have 1 GB RAM, it is advisable to submit data in 250MB or less batch size.    

### Compression

Practicus AI app automatically compresses requests and responses for the model API. You can also compress using 'lz4', 'zlib', 'deflate', 'gzip' compression algorithms. All you need to do is to compress, and send the algorithm using 'content-encoding' http header, or by simply naming the attached file with the compression extension. E.g. my_data.lz4

### Model Metadata

You can learn more about any AI model by simply requesting it's meta data using ?get_meta=true query string. E.g. https://practicus.company.com/models/marketing/churn?get_meta=true

### Sample Python code

```python
import requests
headers = {'authorization': 'Bearer _your_access_token_'}
api_url = 'https://practicus.company.com/models/marketing/churn/'
r = requests.get(api_url + '?get_meta=true', headers=headers)
print('Model details: ', r.text)
r = requests.get(api_url, headers=headers, files={'data.csv': open('data.csv', 'rb')})
print('Prediction result: ', r.text)
```

### Streaming code

By setting the necessary http request headers you can submit the data using as a stream. 

```python
import requests
headers = {'authorization': 'Bearer _your_access_token_',
           'content-type': 'application/octet-stream',
           'content-disposition': 'attachment; filename=data.csv',
           'content-encoding': 'text/csv'}
api_url = 'https://practicus.company.com/models/marketing/churn/'
r = requests.get(api_url, headers=headers, data=open('data.csv', 'rb'), stream=True)
print('Prediction result: ', r.text)
```

### Compression code

With or without streaming, you can submit the data after compressing with lz4', 'zlib', 'deflate', 'gzip' algorithms. If you compress the request, the response will also arrive using the same compression algorithm. 

```python
import lz4.frame
import requests

headers = {'authorization': 'Bearer _your_access_token_',
           'content-type': 'application/octet-stream',
           'content-disposition': 'attachment; filename=data.lz4',
           'content-encoding': 'lz4'}
api_url = 'https://practicus.company.com/models/marketing/churn/'
data = lz4.frame.compress(some_bytes)
r = requests.get(api_url, headers=headers, data=data, stream=True)
print('Prediction result: ', r.text)
```


### Pandas and compression code

It is a very common scenario to submit a pandas dataframe and add the response back to the original dataframe as a new column.


```python
import pandas as pd 
import requests
import lz4.frame

my_df = pd.read_csv('some_data.csv')

headers = {'authorization': 'Bearer _your_access_token_',
           'content-type': 'application/octet-stream',
           'content-disposition': 'attachment; filename=data.lz4',
           'content-encoding': 'lz4'}

api_url = 'https://practicus.company.com/models/marketing/churn/'
data = lz4.frame.compress(my_df.to_string().encode())
r = requests.get(api_url, headers=headers, data=data, stream=True)
...
```