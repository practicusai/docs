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

# LangChain Pipeline Development

The `ChatPracticus` library seamlessly integrates Practicus AI’s hosted private LLM models into the [LangChain](https://github.com/langchain-ai/langchain) framework. This allows you to easily interact with language models that are privately hosted and secured within the Practicus AI environment.

To get started with `ChatPracticus`, you will need the following parameters:

- **endpoint_url:** The API endpoint for the LLM model host.
- **api_token:** A secret key required to authenticate with the model host API.
- **model_id:** The identifier of the target LLM model.

Once these parameters are set, you can define a `chat` instance using `ChatPracticus` and invoke it with any prompt of your choice.

Below is an example of how to create and use a `ChatPracticus` instance in your code.

```python
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_practicus import ChatPracticus

def test_langchain_practicus(api_url, token, inputs):
    chat = ChatPracticus(
        endpoint_url=api_url,
        api_token=token,
        model_id="some models will ignore this",
        stream = True
    )
    
    response = chat.invoke(input=inputs)

    print("\n\nReceived response:\n", response)
    print("\n\nReceived Content:\n", response.content)
```

<!-- #region -->
Async calls also work using the below (but not on jupyter)

```python
import asyncio
asyncio.run(llm.ainvoke([sys_input, human_input1, human_input2]))
print(response)
```
<!-- #endregion -->

After defining your token and API URL, you can easily incorporate prompts into your workflow. By using the `langchain` library, you can structure your messages as follows:

- **System Messages:** Use `SystemMessage` to provide overarching instructions or context that guide the LLM’s behavior.
- **Human Messages:** Wrap user prompts and queries with `HumanMessage` to represent the user’s input.

This structured approach ensures that the model receives clear, role-specific instructions, enhancing the quality and relevance of its responses.

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

#### Received json response:

```text
{
    content="Albert Einstein was a theoretical physicist born on March 14, 1879, in Ulm, in the Kingdom of Württemberg in the German Empire. He is best known for developing the theory of relativity, which revolutionized the understanding of space, time, and energy. His most famous equation, E=mc², expresses the equivalence of mass and energy.\n\nEinstein's work laid the foundation for much of modern physics and he received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect, which was pivotal in the development of quantum theory. Beyond his scientific contributions, Einstein was also known for his philosophical views, advocacy for civil rights, and his involvement in political and humanitarian causes. He passed away on April 18, 1955, in Princeton, New Jersey, USA." 

    ... with additional metadata 
}       
```


---

**Previous**: [Building Visual Apps](../apps/building-visual-apps.md) | **Next**: [Streaming](streaming.md)
