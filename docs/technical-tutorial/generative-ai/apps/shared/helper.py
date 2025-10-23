# You can hold "global" state that can be shared across your APIs, and UI pages.
# You might use this for database connections, caches, or config.
# Keep in mind that global state is simple but also has tradeoffs:
#   - It is shared by all requests and all APIs
#   - You must be careful about concurrency and mutability


class AppState:
    # A trivial shared variable (string) with a default value.
    # Any API or initialization code can read or overwrite this.
    shared_variable: str = "empty"


def some_function():
    return "And, this text is from a shared function."
