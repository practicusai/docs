Welcome to Practicus AI Model API documentation. You can use the [Practicus AI App](https://practicus.ai) or the SDK to build, distribute and deploy AI/ML models and then consume these models with the app or any other REST API compatible system.

### Model prefixes

Practicus AI models are **logically** grouped with the model prefix concept using the https:// [some.address.com] / [some/model/prefix] / [model-name] / [optional-version] / format. E.g. https://practicus.company.com/models/marketing/churn/v6/ can be a model API address where _models/marketing_ is the prefix, _churn_ is the model, and _v6_ is the optional version.

### Model Documentation

Models under a prefix can be viewed by using Practicus AI App. If your admin enabled them, you can also view the documentation by visiting _../prefix/redoc/_ or _../prefix/docs/_ or E.g. https://practicus.company.com/models/marketing/redoc/

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
headers = {
    'authorization': 'Bearer _your_access_token_',
    'content-type': 'text/csv'
}
r = requests.post('https://practicus.company.com/models/marketing/churn/', headers=headers, data=some_csv_data)
print('Prediction result: ', r.text)
```


### Getting session and access API tokens 

Please prefer a 'short-lived' session API access token where you can get one programmatically like the below example.
If you do not use Practicus AI SDK, you can request a 'long-lived' API access token from a Practicus AI admin as well. 
Please note that session tokens will offer increased security due to their short lifetime.  

```python
import practicuscore as prt 
token = prt.models.get_session_token('https://practicus.company.com/models/marketing/churn/')
```

### Compression code

With or without streaming, you can submit the data after compressing with lz4', 'zlib', 'deflate', 'gzip' algorithms. If you compress the request, the response will also arrive using the same compression algorithm. 

```python
import lz4 

headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'text/csv',
    'content-encoding': 'lz4'
}
data_csv = df.to_csv(index=False)
compressed = lz4.frame.compress(data_csv.encode())
print(f"DataFrame compressed from {len(data_csv)} bytes to {len(compressed)} bytes")

r = requests.post(api_url, headers=headers, data=compressed)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

decompressed = lz4.frame.decompress(r.content)
print(f"Result de-compressed from {len(r.content)} bytes to {len(decompressed)} bytes")

pred_df = pd.read_csv(BytesIO(decompressed))

print("Prediction Result:")
pred_df.head()
```
