import os


def load_environment(env_type: str = "") -> None:
    """
    Load environment variables from a .env file.
    If no file is specified, it will load the default .env file in the current directory.
    **Parameters:**
    env_type (str): The type of environment to load. If not specified, it will load the default .env file.
    """
    from dotenv import load_dotenv
    if not env_type:
        load_dotenv()
    else:
        env_file = f".env.{env_type}"
        # Check if file exists in working directory
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"The file {env_file} does not exist in the working directory ({os.getcwd()}).")
        load_dotenv(dotenv_path=env_file)