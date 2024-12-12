---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
import os
import requests

# Create the GitHub API URL
url = 'https://api.github.com/repos/practicusai/sample-data/contents/FAQ_Sample?ref=main'

# Call the API
response = requests.get(url)
if response.status_code == 200:
    files = response.json()  # Get response in JSON format
    
    for file in files:
        file_url = file['download_url']
        file_name = file['name']
        
        # Download files
        file_response = requests.get(file_url)
        if file_response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(file_response.content)
            print(f"'{file_name}' successfully downloaded.")
        else:
            print(f"'{file_name}' file failed to download.")
else:
    print(f"Failed to retrieve data from API, HTTP status: {response.status_code}")

```


---

**Previous**: [Connections](../not-categorized/connections.md) | **Next**: [Lang Chain LLM Model](lang-chain-llm-model.md)
