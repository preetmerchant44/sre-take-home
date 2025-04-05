# API Endpoint Health Monitor

This Python script continuously checks the health of multiple API endpoints defined in a YAML configuration file. It prints out each domain's **availability percentage**, based on both HTTP response status (2xx) and request latency (≤ 500ms).

---

## Requirements

- Python 3.7+
- Install the dependencies using `pip`:
```bash
pip install requests pyyaml
```

---

## How to Run

```bash
python main.py config.yml
```

---

## Issue Identification & Code Improvements

This section outlines the **issues identified** in the original version of the script and **why** specific changes were made in the updated version.

---

### 1. **Unvalidated JSON Body Input**

- **Issue Identified**: The original script directly passed the `body` to `requests.request()` without validating if it's a **valid JSON string**.
- **Why it's a problem**: If the user provides a malformed JSON string (e.g., missing quotes or brackets), it would raise an exception and possibly crash the script or mark the request incorrectly.
- **Change Made**: The updated code attempts to parse the body using `json.loads()`. If parsing fails, the endpoint is marked as `"DOWN"` safely, avoiding script failure:
  ```python
  try:
      json_body = json.loads(body)
  except json.JSONDecodeError:
      return "DOWN"
  ```

---

### 2. **No Response Time Check**

- **Issue Identified**: The original code only checked if the HTTP status code was in the 2xx range, but it didn’t account for **slow or hanging endpoints**.
- **Why it's a problem**: A healthy service should not only respond successfully but also do so within a reasonable amount of time.
- **Change Made**: The updated code measures the **elapsed time** for each request and only considers responses as `"UP"` if they:
  - Return HTTP 2xx **and**
  - Respond within **≤ 500 milliseconds**
  ```python
  elapsed_ms = (time.perf_counter() - start) * 1000
  if 200 <= response.status_code < 300 and elapsed_ms <= 500:
      return "UP"
  ```

---

### 3. **No Timeout Handling**

- **Issue Identified**: The original code didn’t specify a timeout in the `requests.request()` call.
- **Why it's a problem**: If a service hangs or is unreachable, the script could be blocked indefinitely, affecting the monitoring frequency and responsiveness.
- **Change Made**: A timeout of **0.5 seconds** was added to ensure quick feedback and consistent polling intervals:
  ```python
  response = requests.request(..., timeout=0.5)
  ```

---

### 4. **Unsafe Domain Extraction Logic**

- **Issue Identified**: The original code used simple string slicing/splitting to extract the domain name:
  ```python
  domain = endpoint["url"].split("//")[-1].split("/")[0]
  ```
- **Why it's a problem**: This can break with edge cases like:
  - URLs with query strings
  - URLs without `https://`
  - URLs containing port numbers (e.g., `:8080`)
- **Change Made**: Replaced with `urlparse()` from Python’s standard `urllib.parse`, which is more robust and reliable:
  ```python
  from urllib.parse import urlparse
  parsed = urlparse(url)
  return parsed.hostname
  ```

---

### 5. **Ambiguous Loop Statistics**

- **Issue Identified**: The script continuously accumulates availability stats in an infinite loop (`while True:`) without making it clear that the percentage is **cumulative**.
- **Why it's a problem**: The printed "availability percentage" may mislead users if they assume it's **per 15-second interval** rather than cumulative.
- **Change Made**: Added documentation and clarified the calculation. Also suggested (optional) modification to reset `domain_stats` inside the loop to make stats per-iteration if needed:
  ```python
  domain_stats = defaultdict(...)  # inside while True for per-iteration stats
  ```

---

### 6. **Missing Command-Line Argument Check**
- **Issue Identified**: The original script assumes that the config file path is always passed as a command-line argument, but if it’s missing, it could fail silently or crash.
- **Why it's a problem**: This affects the **usability** and **robustness** of the CLI.
- **Change Made**: Added a check for the presence of the config file argument and a user-friendly usage message:
  ```python
  if len(sys.argv) != 2:
      print("Usage: python main.py <config_file_path>")
      sys.exit(1)
  ```

---

## Features

- Supports `GET`, `POST`, and other HTTP methods.
- Custom headers and JSON bodies supported.
- Calculates per-domain availability.
- Tracks both uptime and response time.

---

## Potential Future Enhancements

- Alerting (Slack, email) when endpoints are down.
- Log historical availability to a file or database.
- Support concurrency with asyncio or threading.
- Display a live dashboard or visual graph.

---