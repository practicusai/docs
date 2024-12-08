---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Langchain pipeline development


By using 'ChatPracticus' it is possible to create llm models which can be used in langchains.

ChatPracticus method could take the variables down below:
- endpoint_url: the api url of llm modelhost
- api_token: the secret key to reach llm modelhost api
- model_id: the model id of the model which is intended to use

After defining a 'chat' by using 'ChatPracticus', the chat can be invoked with desired prompts.

Now, let's write a function which will use 'ChatPracticus' method.

```python
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_practicus import ChatPracticus

def test_langchain_practicus(api_url, token, inputs):
    chat = ChatPracticus(
        endpoint_url=api_url,
        api_token=token,
        model_id="current models ignore this",
        stream = True
    )
    
    response = chat.invoke(input=inputs)

    print("\n\nReceived response:\n", response)
    print("\n\nReceived Content:\n", response.content)
```

Async also works, but not on jupyter,

```
import asyncio
asyncio.run(llm.ainvoke([sys_input, human_input1, human_input2]))
print(response)
```


After defining token and api url, we could insert our desired prompts. We could send our messages within 'HumanMessage' while sending our system message by wraping them with 'SystemMessage' methods of 'langchain' library.

```python
import practicuscore as prt
```

```python
region = prt.get_region()

my_model_list = region.model_list
display(my_model_list.to_pandas())
model_name = my_model_list[0].name
print("Using first model name:", model_name)
```

```python
my_app_list = region.app_list
display(my_app_list.to_pandas())
app_name = my_app_list[0].name
print("Using first app name:", app_name)
```

```python
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())
model_prefix = my_model_prefixes[0].key
print("Using first prefix:", model_prefix)
```

```python
host = 'company.practicus.io' # Example url -> 'company.practicus.io'
api_url = f"https://{host}/{model_prefix}/{model_name}/"
token = prt.models.get_session_token(api_url=api_url)
```

```python
human_input1 = HumanMessage("Capital of United Kingdom?")
human_input2 = HumanMessage("And things to do there?")
system_message = SystemMessage("Less 50 words.")

inputs = [human_input1, human_input2, system_message]
```

```python
test_langchain_practicus(api_url, token, ['who is einstein'])
```

<!-- #region -->
#### Received response:
 content="Albert Einstein was a theoretical physicist born on March 14, 1879, in Ulm, in the Kingdom of Württemberg in the German Empire. He is best known for developing the theory of relativity, which revolutionized the understanding of space, time, and energy. His most famous equation, E=mc², expresses the equivalence of mass and energy.\n\nEinstein's work laid the foundation for much of modern physics and he received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect, which was pivotal in the development of quantum theory. Beyond his scientific contributions, Einstein was also known for his philosophical views, advocacy for civil rights, and his involvement in political and humanitarian causes. He passed away on April 18, 1955, in Princeton, New Jersey, USA." response_metadata={'model_id': 'current models ignore this'} id='run-12ae83b4-ec3e-4f5f-a9e2-3577fd4a2ff9-0' usage_metadata={'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}


#### Content:
 Albert Einstein was a theoretical physicist born on March 14, 1879, in Ulm, in the Kingdom of Württemberg in the German Empire. He is best known for developing the theory of relativity, which revolutionized the understanding of space, time, and energy. His most famous equation, E=mc², expresses the equivalence of mass and energy.

Einstein's work laid the foundation for much of modern physics and he received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect, which was pivotal in the development of quantum theory. Beyond his scientific contributions, Einstein was also known for his philosophical views, advocacy for civil rights, and his involvement in political and humanitarian causes. He passed away on April 18, 1955, in Princeton, New Jersey, USA.
<!-- #endregion -->

```python

```


---

**Previous**: [Langchain With Streaming](langchain_with_streaming.md) | **Next**: [Build](../03_llm_apps/01_api_llm_apphost/build.md)
