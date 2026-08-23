# Batch Processing & Rate Limit Handling

## Why `tenacity` for Batch Transcription?
When processing large numbers of files (e.g., 1000 MP3s) against Google Gemini or VectorEngine APIs, the service will inevitably return HTTP 429 (Too Many Requests) or HTTP 500+ errors as server load fluctuates.

Instead of writing custom `time.sleep()` loops and tracking retries manually, we use the `tenacity` Python library to implement **Exponential Backoff**.

## Implementation Details in `scripts/transcribe.py`

```python
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

class RateLimitException(Exception):
    pass

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60), 
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type((requests.exceptions.RequestException, RateLimitException))
)
def transcribe_google(prompt, media_path=None, media_type="audio", temperature=0.0):
    # ...
    if response.status_code == 429 or response.status_code >= 500:
        raise RateLimitException(f"API Error {response.status_code}")
```

- **wait_exponential**: The wait time between retries doubles on each failure (e.g., 4s -> 8s -> 16s), up to a max of 60 seconds. This avoids DDoSing the provider.
- **stop_after_attempt(5)**: Stops hammering the API after 5 total tries, marking that file as a failure.
- **Thread Pool**: We wrap calls to this retry-enabled function in a `concurrent.futures.ThreadPoolExecutor` which allows up to `--workers` (default 5) concurrent processing threads.

## Safe Resuming
Because a batch operation might be manually aborted or eventually fail the retry limits, we must NEVER overwrite already generated `.txt` files on subsequent reruns. The executor checks `os.path.exists("<filename>.txt")` and skips transcription immediately. This allows purely incremental continuation of failed batches.
