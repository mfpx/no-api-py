import json
import math
import random
import time
from os import getenv
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import defaultdict, deque
from threading import Lock

# Rate limiting parameters
max_reqs = getenv("NOAPI_MAX_REQUESTS")
MAX_REQUESTS = int(max_reqs) if max_reqs and max_reqs.isdigit() else 5
# Maximum requests

check_time = getenv("NOAPI_TIME_WINDOW")
TIME_WINDOW = int(check_time) if check_time and check_time.isdigit() else 10
# Time window

block_duration = getenv("NOAPI_BLOCK_DURATION")
BLOCK_DURATION = int(block_duration) if block_duration and block_duration.isdigit() else 60
# Seconds blocked for exceeding

# Track request timestamps and block expiration
request_log = defaultdict(lambda: deque())
blocked_ips = {}

# Thread safety
state_lock = Lock()

class Parser:
    """
    Parser() does what a parser does.
    """

    # Load the no reasons list
    @lru_cache(maxsize=1)
    @staticmethod
    def get_reasons_file(file: str = "reasons.json") -> list[str]:
        with open(file, "r", encoding = "utf-8") as f:
            readfile = f.read()

        return json.loads(readfile)

    @classmethod
    def get_random(cls) -> str:
        """
        Get a random reason each time
        
        :returns: ``str``. A random reason string.
        """

        return random.choice(cls.get_reasons_file())

class JSONHandler(BaseHTTPRequestHandler):
    """
    JSONHandler handles JSON operations.
    """

    def rate_limited(self, client_ip: str) -> tuple[bool, int]:
        """
        Checks if the current client is being rate limited.

        :param client_ip: Client's IP as a string.
        :returns: ``tuple`` - Is client being rate limited and timer.
        """
        now = time.time()

        with state_lock:
            # If blocked, get retry_after safely
            expiry = blocked_ips.get(client_ip)
            if expiry is not None:
                if now < expiry:
                    retry_after = max(0, math.ceil(expiry - now))
                    return True, retry_after
                else:
                    blocked_ips.pop(client_ip, None)

            timestamps = request_log[client_ip]

            # Clean up old timestamps
            cutoff = now - TIME_WINDOW
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            # Enforce limit
            if len(timestamps) >= MAX_REQUESTS:
                expiry = now + BLOCK_DURATION
                blocked_ips[client_ip] = expiry
                timestamps.clear()
                retry_after = max(0, math.ceil(expiry - now))
                return True, retry_after

            timestamps.append(now)
            return False, 0

    def do_GET(self) -> None:
        """
        Default hook for http.server's GET method.

        :returns: ``None``
        """
        client_ip = self.client_address[0]
        limited, retry_after = self.rate_limited(client_ip)

        if limited:
            response = json.dumps({"reason": "Too many requests. Calm down.", "retry_after": retry_after}).encode("utf-8")

            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.send_header("Retry-After",  str(retry_after))
            self.end_headers()
            self.wfile.write(response)
            return

        if random.random() < 0.01:
            reason = "Ugh... fine... I'll do something productive I guess."
            content = {"reason": reason, "sigh": True}

            self.send_response(200)
        else:
            reason = Parser.get_random()
            content = {"reason": reason}

            self.send_response(406)

        response = json.dumps(content).encode("utf-8")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        print(f"Response > {reason}")

# Function to run the server
def run(server_class: type[ThreadingHTTPServer] = ThreadingHTTPServer, handler_class: type[BaseHTTPRequestHandler] = JSONHandler, port: int = 8000) -> None:
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server on port {port}...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nCaught interrupt, shutting down...")
    finally:
        httpd.shutdown()
        httpd.server_close()

if __name__ == "__main__":
    env_port = getenv("NOAPI_PORT", "8000")

    port = int(env_port) if env_port and env_port.isdigit() else 8000
    run(port = port)
