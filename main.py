import yaml
import requests
import time
import json
from collections import defaultdict
from urllib.parse import urlparse

# Function to load configuration from the YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def get_base_domain(url):
    parsed = urlparse(url)
    return parsed.hostname

def check_health(endpoint):
    url = endpoint['url']
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers')
    body = endpoint.get('body')

    # Convert body string to JSON if it exists
    json_body = None
    if body:
        try:
            json_body = json.loads(body)
        except json.JSONDecodeError:
            return "DOWN"  # invalid JSON body

    try:
        start = time.perf_counter()
        response = requests.request(method, url, headers=headers, json=json_body, timeout=0.5)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if 200 <= response.status_code < 300 and elapsed_ms <= 500:
            return "UP"
    except (requests.RequestException, requests.Timeout):
        pass

    return "DOWN"

# Main function to monitor endpoints
def monitor_endpoints(file_path):
    config = load_config(file_path)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    while True:
        for endpoint in config:
            domain = get_base_domain(endpoint["url"])
            result = check_health(endpoint)

            domain_stats[domain]["total"] += 1
            if result == "UP":
                domain_stats[domain]["up"] += 1

        # Log cumulative availability percentages
        for domain, stats in domain_stats.items():
            availability = int(100 * stats["up"] / stats["total"])
            print(f"{domain} has {availability}% availability percentage")

        print("---")
        time.sleep(15)

# Entry point of the program
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file_path>")
        sys.exit(1)

    try:
        monitor_endpoints(sys.argv[1])
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")