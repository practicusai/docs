---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
---

# Using embeddings with Langchain

This examples utilizes Langchain to use Practicus AI hosted embeddings. Practicus AI embeddings are by default OpenAI API compatible.

```python
# Parameters
model_api_url = None
embedding_api_url = None
```

```python
assert model_api_url, "Please select the model API url"
assert embedding_api_url, "Please select the embedding API url"
```

```python
import practicuscore as prt

# Get a new token, or reuse existing, if not expired
try:
    model_api_token = prt.models.get_session_token(api_url=model_api_url)
    embedding_api_token = prt.models.get_session_token(api_url=embedding_api_url)
except:
    model_api_token = None
    embedding_api_token = None
```

```python
# Dummy retriever simulating a vector store

from typing import List
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document


class DummyRetriever(BaseRetriever):
    """A dummy retriever that returns predefined documents."""

    documents: List[Document]

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Return the predefined documents regardless of the query."""
        return self.documents

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """Return the predefined documents regardless of the query (async)."""
        return self.documents
```

```python
import os
from langchain_core.documents import Document
from langchain_practicus import ChatPracticus, PracticusEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# Set your API endpoints and tokens as environment variables or directly
os.environ["PRT_MODEL_API_ENDPOINT_URL"] = model_api_url
os.environ["PRT_MODEL_API_TOKEN"] = model_api_token
os.environ["PRT_EMBED_API_ENDPOINT_URL"] = embedding_api_url
os.environ["PRT_EMBED_API_TOKEN"] = embedding_api_token

# 1. Initialize PracticusEmbeddings
embeddings = PracticusEmbeddings()

# 2. Create sample documents
documents = [
    Document(
        page_content="LangChain Practicus is a library for building applications with private models."
    ),
    Document(
        page_content="It provides tools for working with embeddings and chat models."
    ),
    Document(page_content="You can use it to create powerful AI-powered applications."),
]

# 3. Initialize DummyRetriever
retriever = DummyRetriever(documents=documents)

# 4. Initialize ChatPracticus
llm = ChatPracticus(model_id="your_model_id")  # replace with your model id.

# 5. Create a RetrievalQA chain
prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": PROMPT},
)

# 6. Run the chain
query = "What is LangChain Practicus?"
result = qa_chain.invoke(query)
print(f"Question: {query}")
print(f"Answer: {result}")

# 7. Example of directly using ChatPracticus for a simple chat
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Hello, how are you?"),
]

response = llm.invoke(messages)
print(f"\nChatbot Response: {response.content}")

# 8. Example of using PracticusEmbeddings directly:
texts_to_embed = ["Sample text 1", "Sample text 2"]
embedded_vectors = embeddings.embed_documents(texts_to_embed)
print(f"\nEmbedded Vectors: {embedded_vectors}")

# 9. Example of using PracticusEmbeddings for a single query:
single_query = "Embed this query."
embedded_query_vector = embeddings.embed_query(single_query)
print(f"\nEmbedded Query Vector: {embedded_query_vector}")
```

```python

```


## Supplementary Files

### langchain_serving/model.py
```python
from practicuscore.gen_ai import PrtLangRequest, PrtLangResponse
import json

model = None


async def init(model_meta=None, *args, **kwargs):
    print("Initializing model")
    global model
    # Initialize your LLM model as usual


async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")
    # Add your clean-up code here


async def predict(payload_dict: dict, **kwargs):
    try:
        req = PrtLangRequest.model_validate(payload_dict)
    except Exception as ex:
        raise ValueError(f"Invalid PrtLangRequest request. {ex}") from ex

    # Converts the validated request object to a dictionary.
    data_js = req.model_dump_json(indent=2, exclude_unset=True)
    payload = json.loads(data_js)

    # Joins the content field from all messages in the payload to form the prompt string.
    prompt = " ".join([item["content"] for item in payload["messages"]])

    answer = f"You asked:\n{prompt}\nAnd I don't know how to respond yet."

    resp = PrtLangResponse(
        content=answer,
        lang_model=payload["lang_model"],
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        # additional_kwargs={
        #     "some_additional_info": "test 123",
        # },
    )

    return resp

```


---

**Previous**: [Streaming](streaming.md) | **Next**: [LangChain Serving > Build](langchain-serving/build.md)
