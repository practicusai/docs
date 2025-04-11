---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
host = None  # E.g. 'company.practicus.com'
embedding_model_path = None
model_name = None
model_prefix = None

vector_store = None  # ChromaDB or MilvusDB

if vector_store == "MilvusDB":
    milvus_uri = None  # E.g. 'company.practicus.milvus.com'
```

```python
assert host, "Please enter your host url"
assert embedding_model_path, "Please enter your embedding model path."
assert model_name, "Please enter your embedding model_name."
assert model_prefix, "Please enter your embedding model_prefix."

# You can use one of ChromaDB or MilvusDB as vector store
assert vector_store in ["ChromaDB", "MilvusDB"], "Vector store must be 'ChromaDB' or 'MilvusDB'."

if vector_store == "MilvusDB":
    assert "milvus_uri", "Please enter your milvus connection uri"
```

```python
import practicuscore as prt

region = prt.get_region()
```

If you don't know your prefixes and deployments you can check them out by using the SDK like down below:

```python
# Let's list our models and select one of them.
my_model_list = region.model_list
display(my_model_list.to_pandas())
```

```python
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())
```

## Firstly we need install transformers and torch


Run at terminal:

```python
! pip install transformers sentence-transformers langchain langchain-community langchain-milvus chromadb
! pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### pip install transformers sentence-transformers langchain langchain-community chromadb 
- Transformers: It allows you to easily use Transformer-based models (such as BERT, GPT, etc.).-

- Sentence-Transformers: It produces vector representations of sentences using Transformer models.

- LangChain: It is used to manage more complex workflows with language models. 

- Langchain-Community: Contains additional modules and components developed by the community for the LangChain library.

- ChromaDB: Used as a vector database. It is optimized for embeddings and similarity searches.

- PyPDF: A library used to process PDF files with Python. 

### pip install torch --index-url https://download.pytorch.org/whl/cpu
This command is used to install the PyTorch library with CPU support.

Details:

- Torch (PyTorch): A library used for developing machine learning and deep learning models. It offers features such as tensor computations, automatic differentiation, and advanced modeling.
- --index-url https://download.pytorch.org/whl/cpu: This parameter uses a specific index URL to download the CPU version of PyTorch. If you do not want to install a GPU-specific version, this URL is used.

```python
# Prepare data

import os
import requests

repo_owner = "practicusai"
repo_name = "sample-data"
file_path = "hr_assistant"
branch = "main"


url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"


response = requests.get(url)
if response.status_code == 200:
    files = response.json()

    for file in files:
        file_url = file["download_url"]
        file_name = file["name"]

        file_response = requests.get(file_url)
        if file_response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(file_response.content)
            print(f"'{file_name}' successfully downloaded.")
        else:
            print(f"'{file_name}' not successfully downloaded.")
else:
    print(f"HTTP status: {response.status_code}")
```

## Import Libraries

```python
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma

from langchain_practicus import ChatPracticus

import chromadb
import random
import pandas as pd

import warnings

warnings.filterwarnings("ignore")
```

## Define llm api function and call ChatPracticus in this function


### Function: `call_llm_api`

#### Description
This function interacts with the ChatPracticus API to invoke a response from a language model using the provided inputs, API URL, and API token. The function is designed to send data to the API and retrieve the response content.

### Parameters
- **`inputs`**:  
  The input query or data to be sent to the API for processing. This is typically a string or JSON object depending on the API's requirements.

- **`api_url`**:  
  The endpoint URL of the ChatPracticus API. This is the location where the API call will be directed.

- **`api_token`**:  
  The authentication token for accessing the ChatPracticus API. This ensures secure communication and proper authorization.

1. The function initializes a `ChatPracticus` object with the specified API URL and token. The `model_id` parameter is currently unused or ignored but can be included for future model-specific configurations.
   
2. The `invoke` method of the `ChatPracticus` object is called with the given input. This sends the query to the API and retrieves the response.

3. The function returns the `content` attribute of the response, which contains the text generated by the language model.



```python
def call_llm_api(inputs, api_url, api_token):
    # We need to give input to 'generate_response'. This function will use our 'api_token' and 'endpoint_url' and return the response.

    """
    This function will use our 'api_token' and 'api_url' and return the response.

    :params inputs: The input to be sent to the API.
    :params api_url: The endpoint URL of the ChatPracticus API.
    :params api_token: Token of our model.
    """

    chat = ChatPracticus(
        endpoint_url=api_url,
        api_token=api_token,
        model_id="current models ignore this",
    )

    response = chat.invoke(input=inputs)

    return response.content
```

## Get all resumes and use seperator for split questions


1. **`df = pd.read_csv("HR.csv")`**:  
   - Reads the CSV file `HR.csv` into a pandas DataFrame called `df`.  
   - The DataFrame should contain a column named `Resume_str`.

2. **`merged_resumes = ''`**:  
   - Initializes an empty string `merged_resumes`, which will store the concatenated resume data.

3. **For Loop**:
   - Iterates over each resume string in the `Resume_str` column of the DataFrame.  
   - Appends each resume to the `merged_resumes` string, preceded by the delimiter `//m-n-m//`.

#### Final Output
- The variable `merged_resumes` contains all resumes concatenated into a single string, with `//m-n-m//` acting as a separator between each resume.

```python
df = pd.read_csv("HR.csv")
merged_resumes = ""
for resume in df["Resume_str"]:
    merged_resumes = merged_resumes + "//m-n-m//" + resume
```

#### Description
This function processes a concatenated string of resumes, splits them into individual documents based on a delimiter, and further divides these documents into smaller chunks for analysis. The function utilizes a `CharacterTextSplitter` to handle the chunking process.

1. **Split the Resumes**:
   - The input `merged_resumes` is split into individual resume strings using the `//m-n-m//` delimiter.

2. **Create Document Objects**:
   - Each resume is transformed into a `Document` object. Empty or whitespace-only resumes are excluded.

3. **Initialize the Text Splitter**:
   - A `CharacterTextSplitter` is set up with the following configuration:
     - **`separator="//m-n-m//"`**: The delimiter used for splitting.
     - **`chunk_size`**: Controls the maximum size of each text chunk.
     - **`chunk_overlap`**: Adds overlapping text between chunks for better context retention.

4. **Split Documents**:
   - The documents are further divided into smaller chunks using the `CharacterTextSplitter`.

5. **Aggregate Results**:
   - The chunks are appended to the `all_docs` list, which is returned as the final output.

#### Returns
- **`all_docs`**:  
  A list of smaller text chunks, each represented as a document object, ready for further processing.


```python
def load_and_split_resumes(merged_resumes, chunk_size=500, chunk_overlap=50):
    """
    Load and split email strings into chunks.

    :param merged_resumes: A single string containing all resumes contents, separated by '//m-n-m//'.
    :param chunk_size: The maximum number of characters in each text chunk.
    :param chunk_overlap: The number of characters to overlap between consecutive chunks.
    """
    all_docs = []
    text_splitter = CharacterTextSplitter(
        separator="//m-n-m//",  # Defines the separator used to split the text.
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    # Split resumes
    resumes = merged_resumes.split("//m-n-m//")

    # Transform to Document
    documents = [Document(page_content=resume.strip()) for resume in resumes if resume.strip()]

    # Split docs
    split_docs = text_splitter.split_documents(documents)
    all_docs.extend(split_docs)

    return all_docs
```

1. **Function Call**:
   - `load_and_split_resumes(merged_resumes)`:
     - The `merged_resumes` string, containing all resumes concatenated and separated by `//m-n-m//`, is passed to the `load_and_split_resumes` function.
     - This function:
       - Splits the resumes into individual documents.
       - Further chunks each document into smaller pieces based on the defined `chunk_size` and `chunk_overlap` parameters.

2. **Output**:
   - The result of the function is assigned to the variable `text_chunks`.
   - `text_chunks` is a list of chunked text segments, ready for downstream processing or analysis.



```python
# Create our chunks
text_chunks = load_and_split_resumes(merged_resumes)
```

## Create the vector store and model path is given


1. **Condition Check**:
   - `if vector_store == 'ChromaDB':`
     - Ensures that the code block is executed only if `ChromaDB` is selected as the vector store.

2. **`create_chroma_vector_store` Function**:
   - This function generates embeddings for the provided text chunks and creates a Chroma vector store.

3. **Assign Retriever**:
   - `retriever_resumes = create_chroma_vector_store(text_chunks, embedding_model_path)`:
     - Calls the `create_chroma_vector_store` function with `text_chunks` and the embeddings model path to generate the retriever.


```python
if vector_store == "ChromaDB":
    # Generate embeddings and create vector store
    def create_chroma_vector_store(chunks, embeddings_model_path):
        embeddings = HuggingFaceEmbeddings(  # This class is used to generate embeddings for the text chunks.
            model_name=embeddings_model_path,  # Specifies the path to the pre-trained embeddings model used for generating embeddings.
            model_kwargs={"device": "cpu"},  # Configuration for running model on cpu.
            encode_kwargs={"normalize_embeddings": False},
        )

        db_name = str(random.random())
        vectorstore_resumes = Chroma.from_documents(
            collection_name=db_name, documents=chunks, embedding=embeddings
        )  # This method creates a vector store from the provided documents (chunks) and embeddings.

        # 'search_type' parameter defines the method to use while searching the most relevant documents to the prompt and 'k' parameter defines the number of documents which will include within context
        retriever_resumes = vectorstore_resumes.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        return retriever_resumes

    retriever_resumes = create_chroma_vector_store(text_chunks, embedding_model_path)
```

## (OPTIONAL) Milvus Vector DB


1. **Condition Check**:
   - `if vector_store == 'MilvusDB':`
     - Ensures that the Milvus-based vector store logic is executed only when `MilvusDB` is selected.

2. **`create_milvus_vector_store` Function**:
   - This function generates embeddings for the provided text chunks and stores them in a Milvus vector database.

   - **Inputs**:
     - `chunks`: The text chunks to be embedded and stored.
     - `embeddings_model_path`: Path to the pre-trained embeddings model.

   - **Steps**:
     - **Generate Embeddings**:
       - `HuggingFaceEmbeddings` generates embeddings for the text chunks.
       - Parameters:
         - `model_name`: Path to the pre-trained embeddings model.
         - `model_kwargs`: Specifies the device to run the model (`'cpu'` in this case).
         - `encode_kwargs`: Optional configuration for encoding (e.g., `normalize_embeddings`).

     - **Connect to Milvus**:
       - `connections.connect` establishes a connection to the Milvus server.
       - Parameters:
         - `host`: The URI of the Milvus server.
         - `port`: Default port for Milvus, `19530`.

     - **Create Vector Store**:
       - `Milvus.from_documents` creates a vector store with:
         - `documents`: The input text chunks.
         - `embedding`: The generated embeddings.
         - `collection_


```python
from langchain_milvus import Milvus
from pymilvus import connections

if vector_store == "MilvusDB":

    def create_milvus_vector_store(chunks, embeddings_model_path):
        embeddings = HuggingFaceEmbeddings(  # This class is used to generate embeddings for the text chunks.
            model_name=embeddings_model_path,  # Specifies the path to the pre-trained embeddings model used for generating embeddings.
            model_kwargs={"device": "cpu"},  # Configuration for running model on cpu.
            encode_kwargs={"normalize_embeddings": False},
        )

        connections.connect("default", host=milvus_uri, port="19530")

        vectorstore = Milvus.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="langchain_example",
            connection_args={"uri": f"https://{milvus_uri}:19530"},
            drop_old=True,  # Drop the old Milvus collection if it exists
        )

        # 'search_type' parameter defines the method to use while searching the most relevant documents to the prompt and 'k' parameter defines the number of documents which will include within context
        retriever_resumes = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        return retriever_resumes

    retriever_resumes = create_milvus_vector_store(text_chunks, embedding_model_path)
```

## Define format_docs for join all chunks



#### Description
This function processes a list of document objects, extracts their `page_content` attributes, and concatenates all the document contents into a single string. Each document's content is separated by two newline characters (`\n\n`) to enhance readability.

1. **Extract Document Content**:
   - Iterates over the list `docs` and retrieves the `page_content` attribute from each document object.

2. **Join Content**:
   - Combines all extracted content into a single string, with each document's content separated by two newline characters (`\n\n`).

3. **Return Result**:
   - The resulting string is returned for use in other parts of the application.


```python
def format_docs(docs):
    # Retrieves the content of each document in the `docs` list and joins the content of all documents into a single string, with each document's content separated by two newline characters.
    return "\n\n".join(doc.page_content for doc in docs)
```

## All chains merged into each other at this function


#### Description
This function retrieves relevant documents for a given question using a retriever, formats a prompt with the documents and question, and queries a language model API to generate an answer.

1. **Define Prompt Template**:
   - A `PromptTemplate` object is created to format the input for the language model.
   - **Template Details**:
     - Includes retrieved context (relevant documents).
     - Contains the question.
     - Instructs the model to respond with "I don't know" if the answer is unavailable.

2. **Retrieve Relevant Documents**:
   - Calls `retriever.get_relevant_documents(question)` to fetch documents most relevant to the provided question.

3. **Format the Retrieved Documents**:
   - The retrieved documents are passed to `format_docs` to be concatenated into a single string, separated by two newline characters.

4. **Construct the Prompt**:
   - The `PromptTemplate` is used to format the prompt with the retrieved context and the question.

5. **Query the API**:
   - Calls the `call_llm_api` function with the formatted prompt, `api_url`, and `api_token` to query the language model.

6. **Extract and Return the Answer**:
   - Extracts the answer from the API response by splitting the output on the keyword `Answer:` and removing extra whitespace.

```python
def query_resume(retriever, question, api_url, api_token):
    prompt_template = PromptTemplate(  # Defines a template for the prompt sent to the LLM.
        input_variables=["context", "question"],
        template=(  # The format of the prompt.
            "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, just say that you don't know.\n"
            "Question: {question}\nContext: {context}\nAnswer:"
        ),
    )

    docs = retriever.get_relevant_documents(
        question
    )  # Uses the retriever to get relevant documents based on the question.
    context = format_docs(docs)  # Formats the retrieved documents

    prompt = prompt_template.format(context=context, question=question)  # Formats the prompt

    answer = call_llm_api(prompt, api_url, api_token)

    return answer.strip().split("Answer:")[-1].strip()
```

## Chat Examples


### Code Explanation

This code snippet imports the `practicuscore` module and retrieves the current region using the `get_region` function.

#### Workflow

1. **Import the Module**:
   - `import practicuscore as prt`:
     - The `practicuscore` library is imported and aliased as `prt` for convenience.
     - This module likely provides utility functions or methods for interacting with Practicus-related resources.

2. **Get the Region**:
   - `region = prt.get_region()`:
     - Calls the `get_region` function from the `practicuscore` module.
     - This function retrieves information about the current region, which may be used for region-specific configurations or operations.


```python
import practicuscore as prt

region = prt.get_region()
```

1. **Construct the API URL**:
   - `api_url = f"https://{host}/{model_prefix}/{model_name}/"`:
     - Uses string formatting to dynamically create the API URL based on:
       - `host`: The base URL or hostname of the server.
       - `model_prefix`: The selected model prefix.
       - `model_name`: The selected model name.
     - The resulting URL specifies the endpoint for accessing the model.

2. **Generate Session Token**:
   - `token = prt.models.get_session_token(api_url=api_url)`:
     - Calls the `get_session_token` function from the `practicuscore.models` module.
     - The `api_url` parameter specifies the endpoint for which the token is generated.
     - The session token ensures secure and authorized communication with the API.


```python
# Create api url and token
api_url = f"https://{host}/{model_prefix}/{model_name}/"
token = prt.models.get_session_token(api_url=api_url)
```

### Create query and print answer

```python
# Example query
answer = query_resume(
    retriever=retriever_resumes,
    question="What are the leadership qualities of an HR Director?",
    api_url=api_url,
    api_token=token,
)
# Get Answer
print(answer)
```


---

**Previous**: [Memory Chabot](../ecomm-sdk/memory-chabot.md) | **Next**: [Deploying LLM > Introduction](../deploying-llm/Introduction.md)
