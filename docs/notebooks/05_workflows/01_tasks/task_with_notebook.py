import practicuscore as prt 

print("Starting to run notebook.")

prt.notebooks.execute_notebook(
    "task_with_notebook",
    # By default failed notebooks will not fail caller and just print result.
    # Since this is a task, let's fail the task too.
    raise_on_failure=True,
)

print("Notebook completed running without issues.")
