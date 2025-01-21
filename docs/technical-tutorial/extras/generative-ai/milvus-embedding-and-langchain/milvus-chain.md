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

## Firstly we need install transformers and torch

In this tutorial we will see how to create a MILVUS vector store for encoded documents and how to store the embeddings in the desired vector store using Practicus AI SDK.

Focuses:
- Preparing test documents
- Creating Milvus Vector Store
- Creating an index
- Inserting embeddings
- Using the vector store within RAG pipeline


Necessary libraries:

```python
! pip install transformers sentence-transformers langchain langchain-community langchain-milvus chromadb pypdf
! pip install torch --index-url https://download.pytorch.org/whl/cpu
```

```python
import practicuscore as prt
from transformers import pipeline
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma

from langchain_practicus import ChatPracticus

import chromadb
import random

import warnings
warnings.filterwarnings('ignore')

region = prt.get_region()
```

### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
host = None # E.g. company.practicus.com'
embedding_model_path = None
milvus_uri = None # E.g. 'company.practicus.milvus.com'
milvus_port = None # E.g. '19530'
model_name = None
model_prefix = None
```

##### If you don't know your prefixes and deployments you can check them out by using the SDK like down below:
 

```python
# Let's list our models and select one of them.
my_model_list = region.model_list
display(my_model_list.to_pandas())

print("Using first model name:", model_name)
# Let's list our prefixes and select one of them.
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())

print("Using first prefix:", model_prefix)
```

```python
assert host, "Please enter your host url"
assert embedding_model_path, "Please enter your embedding model path."
assert milvus_uri, "Please enter your milvus connection uri"
assert milvus_port, "Please enter your milvus connection port"
assert model_name, "Please enter your model_name"
assert model_prefix, "Please enter your model_prefix"
```

## Prepare test document

```python
import requests

url = 'https://raw.githubusercontent.com/practicusai/sample-data/refs/heads/main/small_rag_document/test_document_v1.pdf'

output_file = "test_document_v1.pdf"

# Sending a GET request to the URL
response = requests.get(url)

# Checking if the request was successful
if response.status_code == 200:
    # Writing the file to the specified path
    with open(output_file, "wb") as file:
        file.write(response.content)
    print(f"File downloaded successfully and saved as {output_file}")
else:
    print(f"Failed to download file. HTTP status code: {response.status_code}")
```

## Define llm api function and call ChatPracticus in this function

```python
def call_llm_api(inputs, api_url, api_token):
    """
    This function will use our 'api_token' and 'api_url' and return the response.

    :params inputs: The input to be sent to the API.
    :params api_url: The endpoint URL of the ChatPracticus API.
    
    """

    chat = ChatPracticus(
        endpoint_url=api_url,
        api_token=api_token,
        model_id="current models ignore this",
    )
    
    response = chat.invoke(input=inputs)
    # response = chat.invoke("What is Capital of France?")  # This also works
    
    return(response.content)
```

## Get all pdf files and use seperator for split questions

```python
def load_and_split_pdfs(pdf_files, chunk_size=500, chunk_overlap=50):
    """
    Load all pdf files and split with using the 'seperator'.

    :param pdf_files: A list of paths to the PDF files to be processed.
    :param chunk_size: The maximum number of characters in each text chunk. 
    :param chunk_overlap: The number of characters to overlap between consecutive chunks.
    """
    all_docs = []
    text_splitter = CharacterTextSplitter( # Langchain method used to separate documents, there are different ways
        separator="\n", # Defines the separator used to split the text.
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False)
    
    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file) # PDF loader compatible with langchain
        documents = loader.load_and_split()
        split_docs = text_splitter.split_documents(documents)
        all_docs.extend(split_docs)
            
    return all_docs
```

```python
# Define pdf array
pdf_list = ['test_document_v1.pdf']

text_chunks = load_and_split_pdfs(pdf_list, chunk_size=500)
```

```python
context_array = []
for i, row in enumerate(text_chunks):
    context_array.append(row.page_content)
```

```python
embedding_model = HuggingFaceEmbeddings( # This class is used to generate embeddings for the text chunks.
        model_name=embedding_model_path, # Specifies the path to the pre-trained embeddings model used for generating embeddings.
        model_kwargs={'device': 'cpu'}, # Configuration for running model on cpu.
        encode_kwargs={'normalize_embeddings': False})
```

```python
embeddings = embedding_model.embed_documents(context_array)

vector_dimension = len(embeddings[0])
```

## Create the vector store by using given embedding model

```python
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)
```

### 1. connect to Milvus

Add a new connection alias `default` for Milvus server in `localhost:19530`. 

Actually the `default` alias is a building in PyMilvus. If the address of Milvus is the same as `localhost:19530`, you can omit all parameters and call the method as: `connections.connect()`.

Note: the `using` parameter of the following methods is default to "default".

```python
connections.connect("default", host=milvus_uri, port=milvus_port)
```

### 2. create collection 

We need to create collection with desired fields, in this example our collection will be like down below:

|   |field name   |field type |other attributes                  |  field description      |
|---|:-----------:|:---------:|:--------------------------------:|:-----------------------:|
|1  |"pk"         |VARCHAR    |is_primary=True, auto_id=False    |"primary key field"      |
|2  |"companyInfo"|VARCHAR    |max_length=65535                  |"our text field"         |
|3  |"embeddings" |FloatVector|dim, equals to embedding dimension|"vector field"           |

```python
fields = [
    # Id field of vectors
    FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
    # Embedded texts field
    FieldSchema(name="companyInfo", dtype=DataType.VARCHAR, max_length=65535), # https://milvus.io/docs/limitations.md
    # Embedded vectors field
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=vector_dimension)
]

# Creating schema and collection
schema = CollectionSchema(fields, "dummy_info is a basic example demonstrating document embedding.")
dummy_company_collection = Collection("dummy_info", schema, consistency_level="Strong")
```

### 3. insert data

We need to define our entities which will be inserted into our 'dummy_info' collection and insert them.

The insert() method returns:
- either automatically generated primary keys by Milvus if auto_id=True in the schema;
- or the existing primary key field from the entities if auto_id=False in the schema.

```python
entities = [
    # provide the pk field because `auto_id` is set to False
    [str(i) for i in range(len(text_chunks))], # Will be inserted to first field, 'pk'
    context_array,  # Will be inserted to second field, 'companyInfo'
    embeddings,    # Will be inserted to third field, 'embeddings'
]
```

```python
dummy_company_collection.insert(entities)
```

## 4. Create index

We need to index our inserted entities to creates queries.

In this example we will use Ecludian Distance (L2) and Quantization-based index (IVF_FLAT) as indexing options.

You can check what options do you have from [Milvus Documentation](https://milvus.io/docs/v2.0.x/index.md)

```python
index = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
}

dummy_company_collection.create_index("embeddings", index)
```

## Test the created Milvus DB Collection

After data were inserted into Milvus and indexed, you can perform:
- search based on vector similarity
- query based on scalar filtering(boolean, int, etc.)
- hybrid search based on vector similarity and scalar filtering.

Before conducting a search or a query, you need to load the data in `dummy_info` into memory.

```python
dummy_company_collection.load()
```

```python
# The query down below returns 'companyInfo' field of entities that has any 'pk' information, which means, all of the entities.
entities = dummy_company_collection.query(expr="pk != ''", output_fields=['companyInfo'], limit=100)

# Print out the retrieved entities
for entity in entities:
    print(entity)
```

```python
# Now we can embed a text and querry it on our collection
vector_to_search = embedding_model.embed_documents(['What is the company name?'])
```

```python
import time

search_params = {
    "metric_type": "L2",
    "params": {"nprobe": 10},
}

start_time = time.time()
result = dummy_company_collection.search(vector_to_search, "embeddings", search_params, limit=1, output_fields=["companyInfo"])
end_time = time.time()

for hits in result:
    for hit in hits:
        print(f"hit: {hit}, random field: {hit.entity.get('random')}")
```

### Integration of Milvus DB to RAG pipeline

We use LangChain to integrate our Milvus vector collection into the RAG pipeline for efficient retrieval.

```python
from langchain.vectorstores import Milvus

def initialize_milvus_retriever():

    # Connect to the existing collection in Milvus without recreating it
    milvus_retriever = Milvus(embedding_model, connection_args={"uri": f'https://{milvus_uri}:{milvus_port}'}, collection_name="dummy_info", text_field='companyInfo', vector_field='embeddings')
    return milvus_retriever
```

```python
milvus_retriever = initialize_milvus_retriever()
```

## Define format_docs for join all chunks

```python
def format_docs(docs):
     # Retrieves the content of each document in the `docs` list and joins the content of 
     # all documents into a single string, with each document's content separated by two newline characters.
     return "\n\n".join(doc.page_content for doc in docs) 
```

## All chains merged into each other at this function

```python
# Query the PDF using the API-based LLM
def query_pdf(retriever, question, api_url, api_token):
    """
    this function is used for returning response by using all of the chains we defined above
    
    :param retriever : An instance of a retriever used to fetch relevant documents.
    :param question : The question to be asked about the PDF content.
    """
    
    prompt_template = PromptTemplate( # Defines a template for the prompt sent to the LLM.
        input_variables=["context", "question"],
        template=( # The format of the prompt.
            "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, just say that you don't know.\n"
            "Question: {question}\nContext: {context}\nAnswer:"
        )
    )
    
    docs = retriever.similarity_search(question, k=3) # Uses the retriever to get relevant documents based on the question.
    context = format_docs(docs) # Formats the retrieved documents
    
    prompt = prompt_template.format(context=context, question=question) # Formats the prompt

    answer = call_llm_api(prompt, api_url, api_token)
    
    return answer.strip().split('Answer:')[-1].strip()
```

## Chat Example

```python
api_url = f"https://{host}/{model_prefix}/{model_name}/"
token = prt.models.get_session_token(api_url=api_url)
```

```python
# Example query
answer = query_pdf(retriever = milvus_retriever, 
                   question="What is the name of company?", 
                   api_url = api_url,
                   api_token = token)
print(answer)
```

```python
# Deleting collection after tutorial
utility.drop_collection("dummy_info")
```


---

**Previous**: [Langflow Streamlit Hosting](../llm-apps/langflow-llm-apphost/langflow-streamlit-hosting.md) | **Next**: [Deploying LLM > Introduction](../deploying-llm/Introduction.md)
