---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus_genai
    language: python
    name: python3
---

# LangChain LLM Model: RAG Model for Banking
This notebook demonstrates the development of a **Retrieval-Augmented Generation (RAG)** model for banking-related queries. 
The RAG model retrieves relevant contextual data and generates meaningful answers using a language model. 
We utilize **LangChain**, **Transformers**, and other related libraries to build the model.


### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
host = None  # Example url -> 'company.practicus.com'
embedding_model_path = None
model_name = None
model_prefix = None

vector_store = None

if vector_store == "MilvusDB":
    milvus_uri = None  # Milvus connection url, E.g. 'company.practicus.milvus.com'
```

```python
assert host, "Please enter your host url"
assert embedding_model_path, "Please enter your embedding model path."
assert model_name, "Please enter your embedding model_name."

# You can use one of ChromaDB or MilvusDB as vector store
assert model_prefix, "Please enter your embedding model_prefix."

assert vector_store in ["ChromaDB", "MilvusDB"], "Vector store must be 'ChromaDB' or 'MilvusDB'."
if vector_store == "MilvusDB":
    assert "milvus_uri", "Please enter your milvus connection uri"
```

```python
import practicuscore as prt

region = prt.get_region()
```

```python
vector_store = "MilvusDB"
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

### Preparing Data

```python
import os
import requests

# Create the GitHub API URL
url = "https://api.github.com/repos/practicusai/sample-data/contents/mobile_banking_QA?ref=main"

# Call the API
response = requests.get(url)
if response.status_code == 200:
    files = response.json()  # Get response in JSON format

    for file in files:
        file_url = file["download_url"]
        file_name = file["name"]

        # Download files
        file_response = requests.get(file_url)
        if file_response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(file_response.content)
            print(f"'{file_name}' successfully downloaded.")
        else:
            print(f"'{file_name}' file failed to download.")
else:
    print(f"Failed to retrieve data from API, HTTP status: {response.status_code}")
```

## Libraries Installation
Ensure the necessary libraries are installed using the following commands:

```python
! pip install transformers sentence-transformers langchain langchain-community langchain-milvus chromadb pypdf
! pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Importing Required Libraries
The notebook imports libraries such as Transformers for text processing, LangChain for building components like text splitters and vector stores, and additional utilities for embedding generation and document processing.

```python
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

warnings.filterwarnings("ignore")
```


## Define LLM API Function
A function is defined to interact with the **ChatPracticus** API, sending input prompts and receiving language model-generated responses. 
The API URL and token are required to authenticate and access the service.


```python
def call_llm_api(inputs, api_url, api_token):
    # We need to give input to 'generate_response'. This function will use our 'api_token' and 'endpoint_url' and return the response.

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

    return response.content
```


## Load and Split PDF Files
PDF documents are loaded and split into manageable text chunks using LangChain's `CharacterTextSplitter`. 
This enables the processing of large documents for retrieval tasks.


```python
def load_and_split_pdfs(pdf_files, chunk_size=500, chunk_overlap=50):
    """
    Load all pdf files and split with using the 'seperator'.

    :param pdf_files: A list of paths to the PDF files to be processed.
    :param chunk_size: The maximum number of characters in each text chunk.
    :param chunk_overlap: The number of characters to overlap between consecutive chunks.
    """
    all_docs = []
    text_splitter = (
        CharacterTextSplitter(  # langchain method used to separate documents, there are different methods as well
            separator="  \n \n \n \n",  # Defines the separator used to split the text.
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
    )

    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)  # pdf loader compatible with langchain
        documents = loader.load_and_split()
        split_docs = text_splitter.split_documents(documents)
        all_docs.extend(split_docs)

    return all_docs
```


## Define PDF Files and Process Them
A list of PDF files is specified, and the `load_and_split_pdfs` function processes these files into text chunks for downstream retrieval and analysis.


```python
pdf_list = ["Mobile_Banking_QA.pdf"]

text_chunks = load_and_split_pdfs(pdf_list)
```


## Create Chroma Vector Store
The function creates a **Chroma vector store**, which encodes the text chunks into embeddings using a pre-trained model. 
The vector store allows similarity-based document retrieval.


```python
if vector_store == "ChromaDB":
    # Generate embeddings and create ChromaDB vector store
    def create_chroma_vector_store(chunks, embeddings_model_path):
        embeddings = HuggingFaceEmbeddings(  # This class is used to generate embeddings for the text chunks.
            model_name=embeddings_model_path,  # Specifies the path to the pre-trained embeddings model used for generating embeddings.
            model_kwargs={"device": "cpu"},  # Configuration for running model on cpu.
            encode_kwargs={"normalize_embeddings": False},
        )

        # This method creates a vector store from the provided documents (chunks) and embeddings.
        vectorstore_pdf = Chroma.from_documents(
            collection_name="langchain_example", documents=chunks, embedding=embeddings
        )

        # 'search_type' parameter defines the method to use while searching the most relevant documents to
        # the prompt and 'k' parameter defines the number of documents which will include within context
        retriever_pdf = vectorstore_pdf.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        return retriever_pdf

    retriever_pdf = create_chroma_vector_store(text_chunks, embedding_model_path)
```

## (OPTIONAL) Create Milvus DB
This function creates a vector store in Milvus by generating embeddings for text chunks using a HuggingFace pre-trained model. It connects to the Milvus database, stores the embeddings in a specified collection, and ensures any old collections with the same name are dropped. The resulting vector store is converted into a retriever for similarity-based searches, retrieving the top 2 relevant documents for a query.

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

        connections.connect("default", host=milvus_uri, port="19530")  # Connection to milvus db

        vectorstore = Milvus.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="langchain_example",  # Name for created vector table
            connection_args={
                "uri": f"https://{milvus_uri}:19530"  # Connection configuration to milvus db
            },
            drop_old=True,  # Drop the old Milvus collection if it exists
        )

        # 'search_type' parameter defines the method to use while searching the most relevant documents
        # to the prompt and 'k' parameter defines the number of documents which will include within context
        retriever_pdf = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        return retriever_pdf

    retriever_pdf = create_milvus_vector_store(text_chunks, embedding_model_path)
```


## Format Document Chunks
A utility function combines document chunks into a single string format. 
This formatted text is passed to the language model for querying.


```python
def format_docs(docs):
    # Retrieves the content of each document in the `docs` list and joins the content of all documents into a single string, with each document's content separated by two newline characters.
    return "\n\n".join(doc.page_content for doc in docs)
```


## Query PDF Using LLM
This function combines document retrieval, prompt construction, and LLM inference to answer a given query. 
The RAG model retrieves context from the vector store, formats it, and queries the LLM.


```python
# Query the PDF using the API-based LLM
def query_pdf(retriever, question, api_url, api_token):
    """
    this function is used for returning response by using all of the chains we defined above

    :param retriever : An instance of a retriever used to fetch relevant documents.
    :param question : The question to be asked about the PDF content.
    """

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


## Practicus Integration
Imports the Practicus library, which is used for managing API configurations and token generation for LLM queries.


```python
import practicuscore as prt
```

```python
api_url = f"https://dev.practicus.io/models/llm-proxy/"
token = None  # Get a new token, or reuse existing if not expired.
token = prt.models.get_session_token(api_url=api_url, token=token)
```


## Execute a Sample Query
Demonstrates querying the RAG model with a sample question about banking services. 
The system retrieves relevant context and generates an answer using the integrated LLM.


```python
# Example query
answer = query_pdf(
    retriever=retriever_pdf, question="How can I send money using IBAN", api_url=api_url, api_token=token
)
print(answer)
```

```python
# Example query
answer = query_pdf(
    retriever=retriever_pdf,
    question="My transaction was interrupted at an ATM, where should I apply?",
    api_url=api_url,
    api_token=token,
)
print(answer)
```

```python
# Example query
answer = query_pdf(
    retriever=retriever_pdf, question="can I transfer money between my accounts", api_url=api_url, api_token=token
)
print(answer)
```


---

**Previous**: [Bertscore](../llm-evaluation/BERTScore.md) | **Next**: [LLM Apps > API LLM Apphost > Build](../llm-apps/api-llm-apphost/build.md)
