# pylint: disable=broad-exception-caught

# Standard imports
from functools import wraps
import json
import logging
from typing import Any, Callable, Tuple, TypeVar

# Third party imports
import requests

from utils.truncate_value import truncate_value

# Local imports

F = TypeVar("F", bound=Callable[..., Any])


def handle_exceptions(
    default_return_value: Any = None, raise_on_error: bool = False
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Tuple[Any, ...], **kwargs: Any) -> Any:
            # Create truncated args and kwargs at the beginning
            truncated_args: list[Any] = [truncate_value(arg) for arg in args]
            truncated_kwargs: dict[str, Any] = {
                key: truncate_value(value) for key, value in kwargs.items()
            }

            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as err:
                status_code: int = err.response.status_code

                # Skip logging for 500 Internal Server Error as it's usually a temporary issue and no meaningful information is available
                if status_code == 500:
                    if raise_on_error:
                        raise
                    return default_return_value

                reason: str | Any = err.response.reason
                text: str | Any = err.response.text
                print(f"reason: {reason}, text: {text}, status_code: {status_code}")

                # Ex) 409: Conflict, 422: Unprocessable Entity (No changes made), and etc.
                err_msg = f"{func.__name__} encountered an HTTPError: {err}\n\nArgs: {json.dumps(truncated_args, indent=2)}\n\nKwargs: {json.dumps(truncated_kwargs, indent=2)}\n\nReason: {reason}\n\nText: {text}\n\n"
                logging.error(msg=err_msg)

                if raise_on_error:
                    raise

            except json.JSONDecodeError as err:
                # Get the raw response that caused the JSON decode error
                if hasattr(err, "doc"):
                    raw_response = err.doc
                else:
                    raw_response = "Raw response not available"

                err_msg = f"{func.__name__} encountered a JSONDecodeError: {err}\n\nRaw response: {raw_response}\n\nArgs: {json.dumps(truncated_args, indent=2)}\n\nKwargs: {json.dumps(truncated_kwargs, indent=2)}"
                logging.error(msg=err_msg)
                if raise_on_error:
                    raise

            # Catch all other exceptions
            except (AttributeError, KeyError, TypeError, Exception) as err:
                err_msg = f"{func.__name__} encountered an {type(err).__name__}: {err}\n\nArgs: {json.dumps(truncated_args, indent=2)}\n\nKwargs: {json.dumps(truncated_kwargs, indent=2)}"
                logging.error(msg=err_msg)
                if raise_on_error:
                    raise
            return default_return_value

        return wrapper  # type: ignore[return-value]

    return decorator
