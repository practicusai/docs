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
model_name = "codellama-workshop"
token = "..."

from requests import get
api_url = f'https://practicus.company.com/models/practicus/{model_name}/'
headers = {'authorization': f'Bearer {token}'}
r = get(api_url + '?get_meta=true', headers=headers)

print('Model details: ', r.text)
if r.status_code != 200:
    print(f"Error code {r.status_code}")
    
# r = get(api_url, headers=headers, files={'data.csv': open('data.csv', 'rb')})
# print('Prediction result: ', r.text)
```

```python
def query():
    from datetime import datetime
    from requests import get
    import json
    
    start = datetime.now()
    print("thread start: ", start)
    
    data = {
        'system_context': "",
        'user_prompt': 'Capital of Tanzania'
    }
    r = get(api_url, headers=headers, json=data)
    
    if r.status_code != 200:
        print(f"Error code {r.status_code}")
    
    print('Prediction time (sec): ', (datetime.now() - start).total_seconds())
    print('Prediction result:')
    try:
        parsed = json.loads(r.text)
        print(json.dumps(parsed, indent=1))
    except:
        print(r.text)
    
    print("Headers: ", r.headers)
```

```python
import threading 
from datetime import datetime 

threads = []

thread_start = datetime.now()
for _ in range(5):
    thread = threading.Thread(target=query)
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("Total finished in:", (datetime.now() - thread_start).total_seconds())
```

```python
from datetime import datetime
from requests import get
import json

start = datetime.now()

data = {
    'system_context': 'You answer generic questions',
    'user_prompt': 'tell me what you know about Praticus AI'
    }

r = get(api_url, headers=headers, json=data)

if r.status_code != 200:
    print(f"Error code {r.status_code}")

print('Prediction time (sec): ', (datetime.now() - start).total_seconds())
print('Prediction result:')
try:
    parsed = json.loads(r.text)
    print(json.dumps(parsed, indent=1))
except:
    print(r.text)

print("Headers: ", r.headers)
```

```python
reset_cache_url = "https://practicus.company.com/models/codellama-01/v2/?reset_cache=True"

r = get(reset_cache_url, headers=headers, json=data)

if r.status_code != 200:
    print(f"Error code {r.status_code}")

print(r.text)

print("Headers: ", r.headers)
```


## Supplementary Files

### model.json
```json
{
"download_files_from": "cache/codellama-01/",
"_comment": "you can also define download_files_to otherwise, /var/practicus/cache is used"
}
```

### model.py
```python
import sys
from datetime import datetime

generator = None
answers = ""


async def init(model_meta=None, *args, **kwargs):
    global generator
    if generator is not None:
        print("generator exists, using")
        return

    print("generator is none, building")

    # Assuming llama library is copied into cache dir, in addition to torch .pth files
    llama_cache = "/var/practicus/cache"
    if llama_cache not in sys.path:
        sys.path.insert(0, llama_cache)
        
    try:
        from llama import Llama
    except Exception as e:
        raise ModuleNotFoundError("llama library not found. Have you included it in the object storage cache?") from e
    
    try:
        generator = Llama.build(
            ckpt_dir=f"{llama_cache}/CodeLlama-7b-Instruct/",
            tokenizer_path=f"{llama_cache}/CodeLlama-7b-Instruct/tokenizer.model",
            max_seq_len=512,
            max_batch_size=4,
            model_parallel_size=1
        )
    except:
        building_generator = False
        raise


async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")

    global generator
    generator = None

    from torch import cuda
    cuda.empty_cache()


def _predict(http_request=None, model_meta=None, payload_dict=None, *args, **kwargs):
    start = datetime.now()
    
    # instructions = [[
    #     {"role": "system", "content": payload_dict["system_context"]},
    #     {"role": "user", "content": payload_dict["user_prompt"]}
    # ]]

    instructions = [[
        {"role": "system", "content": ""},
        {"role": "user", "content": "Capital of Turkey"}
    ]]

    results = generator.chat_completion(
        instructions,
        max_gen_len=None,
        temperature=0.2,
        top_p=0.95,
    )

    answer = ""
    for result in results:
        answer += f"{result['generation']['content']}\n"

    print("thread answer:", answer)
    total_time = (datetime.now() - start).total_seconds()
    print("thread asnwer in:", total_time)    

    global answers 
    answers += f"start:{start} end: {datetime.now()} time: {total_time} answer: {answer}\n"


async def predict(http_request, model_meta=None, payload_dict=None, *args, **kwargs):
    await init(model_meta)
    
    import threading 
    
    threads = []

    count = int(payload_dict["count"])
    thread_start = datetime.now()
    for _ in range(count):
        thread = threading.Thread(target=_predict)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    print("Total finished in:", (datetime.now() - thread_start).total_seconds())    

    return {
        "answer": f"Time:{(datetime.now() - thread_start).total_seconds()}\nanswers:{answers}"
    }
    

```


---

**Previous**: [Deploy](05_deploy.md) | **Next**: [Start Cluster](../../05_distributed_computing/01_spark/01_interactive/01_start_cluster.md)
