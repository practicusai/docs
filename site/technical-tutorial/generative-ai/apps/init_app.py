# This file is automatically executed when your APIs App starts up.
# Use it to prepare global state, initialize resources, or connect to services.

# For UI apps, you must manually run `import init_app` in Home.py
# Please keep in mind that global state is *NOT* shared between the UI and API apps.
#   Home.py is a Streamlit App, APIs are hosted via FastAPI.

import practicuscore as prt
from shared.helper import AppState


def initialize() -> None:
    # Log that we are starting initialization
    prt.logger.info("Starting to initialize app.")

    # Example: change a global variable so all APIs can see the new value
    AppState.shared_variable = "changed"

    # Log that initialization is done
    prt.logger.info("Completed initializing app.")


# Run the initializer immediately on import
initialize()
