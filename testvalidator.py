import requests
import json

class APITestValidator:
    def __init__(self, base_url):
        """
        Initialize the API Validator with a base URL for the API.
        """
        self.base_url = base_url

    def test_endpoint(self, endpoint, expected_status=200, expected_keys=None, method="GET", payload=None):
        """
        Test a single endpoint with specified conditions.

        Parameters:
        - endpoint (str): API endpoint to test.
        - expected_status (int): Expected HTTP status code.
        - expected_keys (list): Expected keys in the JSON response.
        - method (str): HTTP method (GET, POST, etc.).
        - payload (dict): Data to send with POST/PUT requests.

        Returns:
        - result (dict): Test result with details.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=payload)
            elif method == "PUT":
                response = requests.put(url, json=payload)
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                raise ValueError("Unsupported HTTP method")

            status_check = response.status_code == expected_status
            content_check = True
            missing_keys = []

            # Check for expected keys in JSON response
            if expected_keys and response.headers.get("Content-Type") == "application/json":
                json_data = response.json()
                content_check = all(key in json_data for key in expected_keys)
                missing_keys = [key for key in expected_keys if key not in json_data]

            # Compile test result
            result = {
                "endpoint": endpoint,
                "method": method,
                "status": response.status_code,
                "expected_status": expected_status,
                "status_check": status_check,
                "content_check": content_check,
                "missing_keys": missing_keys
            }

            if status_check and content_check:
                result["result"] = "PASS"
            else:
                result["result"] = "FAIL"

            return result

        except requests.RequestException as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "error": str(e),
                "result": "ERROR"
            }

    def run_tests(self, endpoints):
        """
        Run tests on a list of endpoints.

        Parameters:
        - endpoints (list): List of endpoint dictionaries with 'endpoint', 'expected_status', 'expected_keys', 'method', and 'payload'.
        """
        results = []
        for ep in endpoints:
            result = self.test_endpoint(
                endpoint=ep['endpoint'],
                expected_status=ep.get('expected_status', 200),
                expected_keys=ep.get('expected_keys', []),
                method=ep.get('method', 'GET'),
                payload=ep.get('payload')
            )
            results.append(result)

        # Print test summary
        print("\nTest Summary:")
        for result in results:
            print(f"Endpoint: {result['endpoint']}, Method: {result['method']}, Result: {result['result']}")
            if result['result'] == "FAIL":
                print(f" - Status Check: {'Pass' if result['status_check'] else 'Fail'}")
                print(f" - Content Check: {'Pass' if result['content_check'] else 'Fail'}")
                if result['missing_keys']:
                    print(f" - Missing Keys: {result['missing_keys']}")
            elif result['result'] == "ERROR":
                print(f" - Error: {result['error']}")

# Define the base URL for the API and test endpoints with expected outcomes
base_url = "https://jsonplaceholder.typicode.com"

# Example endpoints with expected outcomes
endpoints = [
    {
        "endpoint": "/users",
        "expected_status": 200,
        "expected_keys": ["id", "name", "username", "email"],
        "method": "GET"
    },
    {
        "endpoint": "/posts",
        "expected_status": 200,
        "expected_keys": ["id", "title", "body", "userId"],
        "method": "GET"
    },
    {
        "endpoint": "/comments",
        "expected_status": 200,
        "expected_keys": ["id", "name", "email", "body", "postId"],
        "method": "GET"
    }
]

# Create the test validator and run tests
api_validator = APITestValidator(base_url)
api_validator.run_tests(endpoints)
