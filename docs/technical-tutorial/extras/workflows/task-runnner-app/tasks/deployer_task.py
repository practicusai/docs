# Sample Task that the Task Runner App will execute

import practicuscore as prt
from pathlib import Path


def any_file_exists(dir_path: str) -> bool:
    """
    Check if there is at least one file anywhere under the given directory.

    :param dir_path: Path to the directory to be searched.
    :return: True if any file is found, False otherwise.
    """
    base = Path(dir_path)
    return any(p.is_file() for p in base.rglob("*"))


def main():
    prt.logger.info("Starting model deployment task ")

    import os

    assert "DEPLOYMENT_KEY" in os.environ and len(os.environ["DEPLOYMENT_KEY"]) > 0, "DEPLOYMENT_KEY is not provided"
    assert "PREFIX" in os.environ and len(os.environ["PREFIX"]) > 0, "PREFIX is not provided"
    assert "MODEL_NAME" in os.environ and len(os.environ["MODEL_NAME"]) > 0, "MODEL_NAME is not provided"
    assert "MODEL_DIR" in os.environ and len(os.environ["MODEL_DIR"]) > 0, "MODEL_DIR is not provided"

    deployment_key = os.environ["DEPLOYMENT_KEY"]  # "depl"
    prefix = os.environ["PREFIX"]  # models
    model_name = os.environ["MODEL_NAME"]  # sample-model-ro
    model_dir = os.environ["MODEL_DIR"]  # "/home/ubuntu/my/projects/models-repo/sample-model"

    if not any_file_exists(model_dir):
        msg = "Model directory is empty or does not exist. Check logs for details."
        prt.logger.error(msg)
        raise RuntimeError(msg)
    else:
        api_url, api_version_url, api_meta_url = prt.models.deploy(
            deployment_key=deployment_key, prefix=prefix, model_name=model_name, model_dir=model_dir
        )
        prt.logger.info(f"Finished model deployment task successfully. api_url : {api_version_url}")


if __name__ == "__main__":
    main()
