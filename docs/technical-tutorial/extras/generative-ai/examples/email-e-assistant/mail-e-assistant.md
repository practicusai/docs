---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
host = None  # 'E.g. company.practicus.com'
embedding_model_path = None
vector_store = None
milvus_uri = None  # E.g. 'company.practicus.milvus.com'
```

```python
assert host, "Please enter your host url"
assert embedding_model_path, "Please enter your embedding model path."
assert vector_store in ["ChromaDB", "MilvusDB"], "Vector store must be 'ChromaDB' or 'MilvusDB'."
if vector_store == "MilvusDB":
    assert "milvus_uri", "Please enter your milvus connection uri"
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
# Prepare Data
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
    print(f"HTTP Status: {response.status_code}")
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

import warnings

warnings.filterwarnings("ignore")
```


This code initializes and validates the required variables for setting up the environment, including the host URL, embedding model path, and vector store configuration.

1. **Host URL**:
   - `host = None`:
     - Placeholder for the host URL (e.g., `'company.practicus.com'`).
   - `assert host, "Please enter your host url"`:
     - Ensures that a valid host URL is provided. Raises an error with the message `"Please enter your host url"` if `host` is not defined.

2. **Embedding Model Path**:
   - `embedding_model_path = None`:
     - Placeholder for the embedding model's file path.
   - `assert embedding_model_path, "Please enter your embedding model path."`:
     - Ensures that a valid embedding model path is provided. Raises an error if the path is not set.

3. **Vector Store Selection**:
   - `vector_store = None`:
     - Placeholder for selecting a vector store (`'ChromaDB'` or `'MilvusDB'`).
   - `assert vector_store in ['ChromaDB', 'MilvusDB'], "Vector store must be 'ChromaDB' or 'MilvusDB'."`:
     - Ensures that the vector store is either `'ChromaDB'` or `'MilvusDB'`. Raises an error if an invalid option is set.

4. **MilvusDB Configuration (Conditional)**:
   - `if vector_store == 'MilvusDB':`:
     - Executes the following block only if `vector_store` is set to `'MilvusDB'`.
   - `milvus_uri = None`:
     - Placeholder for the Milvus connection URI (e.g., `'company.practicus.milvus.com'`).
   - `assert 'milvus_uri', "Please enter your milvus connection uri"`:
     - Ensures that a valid `milvus_uri` is provided when `MilvusDB` is used.


## Define llm api function and call ChatPracticus in this function


Function interacts with the ChatPracticus API to send input data and retrieve a response using the provided API URL and token.

1. **Initialize ChatPracticus**:
   - `chat = ChatPracticus(...)`:
     - Creates a `ChatPracticus` object with the following parameters:
       - `endpoint_url`: The API endpoint URL.
       - `api_token`: The token for authentication.
       - `model_id`: Currently ignored but reserved for future model-specific configurations.

2. **Invoke the API**:
   - `response = chat.invoke(input=inputs)`:
     - Sends the input data to the API and retrieves the response.

3. **Return the Response**:
   - `return(response.content)`:
     - Extracts and returns the content


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

    return response.content
```

## Get all mails and use seperator for split questions



This code reads a CSV file containing email data, extracts a specific column, and concatenates all messages into a single string, separated by a custom delimiter `//m-n-m//`.

1. **Import pandas**:
   - `import pandas as pd`:
     - Imports the pandas library for data manipulation and analysis.

2. **Read the CSV File**:
   - `df = pd.read_csv('single_sender_1k.csv')`:
     - Reads the CSV file `single_sender_1k.csv` into a pandas DataFrame named `df`.

3. **Select Relevant Column**:
   - `df = df[['message_sent']]`:
     - Filters the DataFrame to include only the `message_sent` column, which contains the email messages.

4. **Initialize Merged String**:
   - `merged_mails = ''`:
     - Initializes an empty string `merged_mails` to store the concatenated messages.

5. **Concatenate Messages**:
   - `for message in df['message_sent']:`:
     - Iterates over each message in the `message_sent` column.
   - `merged_mails = merged_mails + '//m-n-m//' + message`:
     - Appends each message to `merged_mails`, preceded by the delimiter `//m-n-m//`.


```python
import pandas as pd

df = pd.read_csv("single_sender_1k.csv")

df = df[["message_sent"]]

merged_mails = ""

for message in df["message_sent"]:
    merged_mails = merged_mails + "//m-n-m//" + message
```

This function takes a concatenated string of emails, splits it into individual email documents, and further divides the documents into smaller chunks using a specified chunk size and overlap.

1. **Initialize the Text Splitter**:
   - `CharacterTextSplitter` is configured with:
     - **`separator="//m-n-m//"`**: The delimiter used to separate email strings.
     - **`chunk_size`**: The size of each chunk.
     - **`chunk_overlap`**: Overlapping characters between chunks for better context retention.
     - **`length_function=len`**: Uses the `len` function to determine text length.
     - **`is_separator_regex=False`**: Indicates the separator is a literal string, not a regex.

2. **Split Emails**:
   - `emails = merged_mails.split('//m-n-m//')`:
     - Splits the concatenated email string into individual emails using the delimiter.

3. **Transform Emails into Documents**:
   - `documents = [Document(page_content=email.strip()) for email in emails if email.strip()]`:
     - Creates `Document` objects for each email, excluding empty or whitespace-only emails.

4. **Chunk Documents**:
   - `split_docs = text_splitter.split_documents(documents)`:
     - Splits each document into smaller chunks based on the configured `chunk_size` and `chunk_overlap`.

5. **Aggregate Results**:
   - `all_docs.extend(split_docs)`:
     - Adds the resulting chunks to the `all_docs` list.

6. **Return Chunks**:
   - Returns the `all_docs` list containing the split chunks.


```python
def load_and_split_mails(merged_mails, chunk_size=500, chunk_overlap=50):
    """
    Load and split email strings into chunks.

    :param merged_mails: A single string containing all email contents, separated by '//m-n-m//'.
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

    # Split mails
    emails = merged_mails.split("//m-n-m//")

    # Transform to Document
    documents = [Document(page_content=email.strip()) for email in emails if email.strip()]

    # Split docs
    split_docs = text_splitter.split_documents(documents)
    all_docs.extend(split_docs)

    return all_docs
```

## Define pdf array


This code calls the `load_and_split_mails` function to process a concatenated string of emails and generate text chunks for further processing.

1. **Function Call**:
   - `text_chunks = load_and_split_mails(merged_mails)`:
     - Passes the `merged_mails` string to the `load_and_split_mails` function.

2. **Processing Inside the Function**:
   - The `load_and_split_mails` function:
     - Splits the concatenated email string into individual email documents.
     - Further divides each document into smaller chunks based on a specified chunk size and overlap.

3. **Assign the Output**:
   - The resulting list of chunks is assigned to the variable `text_chunks`.

#### Output
- **`text_chunks`**:
  A list of `Document` objects, where each object contains a smaller chunk of email text.


```python
# Create our chunks
text_chunks = load_and_split_mails(merged_mails)
```

## Create the vector store and model path is given


This code generates embeddings for email chunks and creates a ChromaDB vector store to facilitate document retrieval based on similarity.

1. **Check for ChromaDB**:
   - `if vector_store == 'ChromaDB':`:
     - Executes the following block only if `vector_store` is set to `'ChromaDB'`.

2. **Define `create_chroma_vector_store` Function**:
   - This function handles the creation of a vector store using ChromaDB.

3. **Create Vector Store and Retriever**:
   - `retriever_mail = create_chroma_vector_store(text_chunks, embeddings_model_path)`:
     - Calls the `create_chroma_vector_store` function to generate embeddings and create the vector store.




```python
# Generate embeddings and create vector store
if vector_store == "ChromaDB":

    def create_chroma_vector_store(chunks, embeddings_model_path):
        embeddings = HuggingFaceEmbeddings(  # This class is used to generate embeddings for the text chunks.
            model_name=embeddings_model_path,  # Specifies the path to the pre-trained embeddings model used for generating embeddings.
            model_kwargs={"device": "cpu"},  # Configuration for running model on cpu.
            encode_kwargs={"normalize_embeddings": False},
        )

        db_name = str(random.random())
        vectorstore = Chroma.from_documents(
            collection_name=db_name, documents=chunks, embedding=embeddings
        )  # This method creates a vector store from the provided documents (chunks) and embeddings.

        # 'search_type' parameter defines the method to use while searching the most relevant documents to the prompt and 'k' parameter defines the number of documents which will include within context
        retriever_mail = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        return retriever_mail

    retriever_mail = create_chroma_vector_store(text_chunks, embedding_model_path)
```

## (OPTIONAL) Milvus Vector DB


This code sets up a vector store using MilvusDB to store embeddings for email chunks and enables similarity-based document retrieval.

#### Workflow

1. **Check for MilvusDB**:
   - `if vector_store == 'MilvusDB':`
     - Executes the following block only if `vector_store` is set to `'MilvusDB'`.

2. **Define `create_milvus_vector_store` Function**:
   - This function creates a vector store using MilvusDB.

3. **Create Vector Store and Retriever**:
   - `retriever_mail = create_milvus_vector_store(text_chunks, embeddings_model_path)`:
     - Calls the `create_milvus_vector_store` function to set up the Milvus vector store and create the retriever.


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
        retriever_mail = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        return retriever_mail

    retriever_mail = create_milvus_vector_store(text_chunks, embedding_model_path)
```

## Define format_docs for join all chunks


#### Description
This function processes a list of document objects and combines their content into a single string, with each document's content separated by two newline characters (`\n\n`) for readability.

1. **Retrieve Content**:
   - Iterates through the `docs` list to access the `page_content` attribute of each document.

2. **Join Content**:
   - Combines all retrieved content into a single string.
   - Adds two newline characters (`\n\n`) between each document's content to improve separation and readability.

3. **Return Result**:
   - The concatenated string is returned.


```python
def format_docs(docs):
    # Retrieves the content of each document in the `docs` list and joins the content of all documents into a single string, with each document's content separated by two newline characters.
    return "\n\n".join(doc.page_content for doc in docs)
```

## All chains merged into each other at this function


#### Description
This function retrieves relevant documents related to a given question from a retriever, formats them into a prompt, and queries a language model (LLM) API to generate a response.

1. **Define Prompt Template**:
   - Creates a `PromptTemplate` object to format the input for the language model.
   - **Template Details**:
     - Includes retrieved context (relevant documents).
     - Contains the question.
     - Instructs the model to respond with "I don't know" if it cannot answer.

2. **Retrieve Relevant Documents**:
   - `retriever.get_relevant_documents(question)`:
     - Retrieves the most relevant documents for the given question.
   - `format_docs(docs)`:
     - Formats the retrieved documents into a single string, separated by two newline characters (`\n\n`).

3. **Format the Prompt**:
   - `prompt_template.format(context=context, question=question)`:
     - Generates a formatted prompt by inserting the context and question into the template.

4. **Query the LLM API**:
   - `call_llm_api(prompt, api_url, api_token)`:
     - Sends the formatted prompt to the LLM API and retrieves the response.

5. **Extract the Answer**:
   - Extracts the answer from the API response by splitting the output on the keyword `Answer:` and removing extra whitespace.

6. **Return the Answer**:
   - Returns the extracted answer as a string.

```python
# Query the PDF using the API-based LLM
def query_mail(retriever, question, api_url, api_token):
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

## Chat Examples


This code initializes the Practicus environment by retrieving the current region using the `practicuscore` library.

1. **Import PracticusCore**:
   - `import practicuscore as prt`:
     - Imports the `practicuscore` library and assigns it the alias `prt` for easier usage.

2. **Retrieve Region**:
   - `region = prt.get_region()`:
     - Calls the `get_region` function from the `practicuscore` module.
     - This function retrieves the region configuration or information relevant to the Practicus environment.
     - The `region` object typically contains details like available resources, models, or configurations tied to a specific geographic or logical region.

```python
import practicuscore as prt

region = prt.get_region()
```

This code retrieves a list of available models in the current region, displays them in a tabular format, and selects the first model for further use.

1. **Retrieve Model List**:
   - `my_model_list = region.model_list`:
     - Accesses the `model_list` attribute of the `region` object.
     - This attribute contains a list of available models in the region.

2. **Display Model List**:
   - `display(my_model_list.to_pandas())`:
     - Converts the `model_list` to a pandas DataFrame using the `.to_pandas()` method for better visualization.
     - Displays the DataFrame, allowing the user to view details such as model names, versions, and statuses.

3. **Select First Model**:
   - `model_name = my_model_list[0].name`:
     - Accesses the first model in the list using index `0` and retrieves its name using the `.name` attribute.

4. **Print the Selected Model Name**:
   - `print("Using first model name:", model_name)`:
     - Outputs the name of the selected model to the console for verification.

```python
my_model_list = region.model_list
display(my_model_list.to_pandas())
model_name = my_model_list[0].name
print("Using first model name:", model_name)
```

This code retrieves a list of available model prefixes in the current region, displays them in a tabular format, and selects the first prefix for further use.

1. **Retrieve Model Prefix List**:
   - `my_model_prefixes = region.model_prefix_list`:
     - Accesses the `model_prefix_list` attribute of the `region` object.
     - This attribute contains a list of model prefixes available in the region.

2. **Display Model Prefix List**:
   - `display(my_model_prefixes.to_pandas())`:
     - Converts the `model_prefix_list` to a pandas DataFrame using the `.to_pandas()` method for better visualization.
     - Displays the DataFrame, allowing the user to view details such as prefix keys and descriptions.

3. **Select First Prefix**:
   - `model_prefix = my_model_prefixes[0].key`:
     - Accesses the first prefix in the list using index `0` and retrieves its key using the `.key` attribute.

4. **Print the Selected Prefix Key**:
   - `print("Using first prefix:", model_prefix)`:
     - Outputs the selected prefix key to the console for verification.

```python
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())
model_prefix = my_model_prefixes[0].key
print("Using first prefix:", model_prefix)
```

This code constructs an API URL for accessing a model and generates a session token for authenticated communication.

1. **Construct the API URL**:
   - `api_url = f"https://{host}/{model_prefix}/{model_name}/"`:
     - Uses Python's f-string formatting to dynamically create the API URL.
     - Components:
       - **`host`**: The base hostname of the API server.
       - **`model_prefix`**: The selected model prefix.
       - **`model_name`**: The name of the selected model.
     - The resulting URL points to the specific endpoint for the desired model.

2. **Generate a Session Token**:
   - `token = prt.models.get_session_token(api_url=api_url)`:
     - Calls the `get_session_token` method from the `practicuscore.models` module.
     - Parameters:
       - **`api_url`**: The constructed API URL.
     - The session token is returned and stored in the `token` variable.


```python
api_url = f"https://{host}/{model_prefix}/{model_name}/"
token = None  # Get a new token, or reuse existing if not expired.
token = prt.models.get_session_token(api_url=api_url, token=token)
```

Get answer with our function 

```python
# Example query
answer = query_mail(
    retriever=retriever_mail,
    question="How can business meetings be made more productive, and what are some alternative travel suggestions?",
    api_url=api_url,
    api_token=token,
)
print(answer)
```


---

**Previous**: [Memory Chabot](../ecomm-sdk/memory-chabot.md) | **Next**: [Memory Chatbot Sdk > Chatbot-Console-OpenAI](../memory-chatbot-sdk/chatbot-console-openai.md)
