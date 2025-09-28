import os
from dotenv import load_dotenv
import redis

load_dotenv()

host = os.getenv("REDIS_HOST")
port = int(os.getenv("REDIS_PORT", 6379))
username = os.getenv("REDIS_USERNAME")
password = os.getenv("REDIS_PASSWORD")

print(f"Trying to connect to Redis at {host}:{port} with username={username!r}")

# Try non-TLS connection
try:
    client = redis.Redis(host=host, port=port, username=username, password=password, socket_connect_timeout=5)
    pong = client.ping()
    print("Non-TLS ping success:", pong)
except Exception as e:
    print("Non-TLS connection failed:", repr(e))

# Try TLS connection (common with managed Redis)
try:
    client_tls = redis.Redis(host=host, port=port, username=username, password=password, ssl=True, ssl_cert_reqs=None, socket_connect_timeout=5)
    pong = client_tls.ping()
    print("TLS ping success:", pong)
except Exception as e:
    print("TLS connection failed:", repr(e))
