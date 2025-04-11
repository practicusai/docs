import os
import practicuscore as prt


MY_FIRST_ENV = os.getenv("MY_FIRST_ENV", default="?")
MY_SECOND_ENV = os.getenv("MY_SECOND_ENV", default="?")
PERSONAL_SECRET_1 = os.getenv("PERSONAL_SECRET_1", default="?")
SHARED_SECRET_1 = os.getenv("SHARED_SECRET_1", default="?")
# All Practicus AI apps boot at /var/practicus, and your files are copied here.
HELLO_TXT_PATH = "/var/practicus/hello.txt"


@prt.apps.api("/verify")
async def verify(**kwargs):
    hello_txt_content = "?"
    if os.path.exists(HELLO_TXT_PATH):
        with open(HELLO_TXT_PATH, "r") as f:
            hello_txt_content = f.read().strip()

    return {
        "msg": "Reading configuration from OS environment variables. (Only length of secrets for security)",
        "MY_FIRST_ENV": MY_FIRST_ENV,
        "MY_SECOND_ENV": MY_SECOND_ENV,
        "PERSONAL_SECRET_1_LEN": len(PERSONAL_SECRET_1),
        "SHARED_SECRET_1_LEN": len(SHARED_SECRET_1),
        "hello_txt_content": hello_txt_content,
    }
