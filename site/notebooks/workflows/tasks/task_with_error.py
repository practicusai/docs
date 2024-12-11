import practicuscore as prt


def main():
    print("Starting task..")

    # Code as usual:
    # - Process data
    # - Train models
    # - Make predictions
    # - Orchestrate other tasks
    # - ...

    try:
        raise NotImplementedError("Still baking..")
    except Exception as ex:
        # Psudo detail log
        with open("my_log.txt", "wt") as f:
            f.write(str(ex))
        raise ex
    
    print("Finished task..")


if __name__ == '__main__':
    main()