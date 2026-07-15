import os


INTERNET_CONTEXT_ENV_VAR = "ENABLE_INTERNET_CONTEXT"
_TRUTHY_VALUES = {"1", "true", "yes", "on"}


def is_internet_context_enabled() -> bool:
    """Return whether the optional internet-context controls are available."""
    value = os.getenv(INTERNET_CONTEXT_ENV_VAR, "false")
    return value.strip().lower() in _TRUTHY_VALUES
