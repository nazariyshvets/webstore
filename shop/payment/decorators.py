import time
from functools import wraps


def retry(max_retries, initial_delay_seconds=1, backoff_factor=2):
  """
  Decorator function to retry a function in case of failure.

  :param max_retries: Maximum number of retry attempts.
  :param initial_delay_seconds: Initial delay between retries in seconds.
  :param backoff_factor: Factor by which the delay increases with each retry.
  """
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      retries = 0
      delay_seconds = initial_delay_seconds
      last_exception = None
      while retries < max_retries:
        try:
          return func(*args, **kwargs)
        except Exception as e:
          last_exception = e
          print(f"Attempt {retries + 1} failed: {e}")
          retries += 1
          if retries < max_retries:
            # Exponential backoff
            delay_seconds *= backoff_factor
            time.sleep(delay_seconds)
      raise Exception(
          f"Досягнуто максимальну кількість повторних спроб ({max_retries}). Остання помилка: {last_exception}")
    return wrapper
  return decorator


retry_decorator = retry(
    max_retries=3, initial_delay_seconds=1, backoff_factor=2)
