from dotenv import load_dotenv


def load_environment() -> None:
    """
    Load local environment variables from `.env` when present.

    This lets each developer keep their own API keys outside Git while the app
    still reads them through normal environment variables.
    """
    load_dotenv()
