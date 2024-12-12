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

repo_owner = "practicusai"
repo_name = "sample-data"
file_path = "hr_asistant"
branch = "main"


url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"


response = requests.get(url)
if response.status_code == 200:
    files = response.json()  
    
    for file in files:
        file_url = file['download_url'] 
        file_name = file['name']  

        file_response = requests.get(file_url)
        if file_response.status_code == 200:

            with open(file_name, 'wb') as f:
                f.write(file_response.content)
            print(f"'{file_name}' successfully downloaded.")
        else:
            print(f"'{file_name}' not successfully downloaded.")
else:
    print(f"HTTP Status: {response.status_code}")

```


---

**Previous**: [Cv Asistant](../cv-asistant/cv-asistant.md) | **Next**: [Mail E-Assistant](mail-e-assistant.md)
