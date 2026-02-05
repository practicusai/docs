# This file is automatically executed when your APIs App starts up.
# Use it to prepare global state, initialize resources, or connect to services.

# For UI apps, you must manually run `import init_app` in Home.py
# Please keep in mind that global state is *NOT* shared between the Streamlit UI Home.py) and API apps.

import practicuscore as prt
from shared.helper import AppState


def init_app() -> None:
    # Log that we are starting initialization
    prt.logger.info("Starting to initialize app.")

    # Example: change a global variable so all APIs can see the new value
    AppState.shared_variable = "changed"

    # Log that initialization is done
    prt.logger.info("Completed initializing app.")
