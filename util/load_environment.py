

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
        load_dotenv(dotenv_path=env_file)