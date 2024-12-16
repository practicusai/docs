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
    print("thread answer in:", total_time)    

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
    
