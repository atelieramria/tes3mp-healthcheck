import os
from dotenv import load_dotenv
import requests
import socket
import struct
import time

def send_raknet_ping(address, port, timeout, max_retries, retry_delay):
    RAKNET_MAGIC = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
    timestamp = int(time.time() * 1000)
    ping_packet = b'\x01' + struct.pack('>Q', timestamp) + RAKNET_MAGIC
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    for attempt in range(max_retries):
        try:
            sock.sendto(ping_packet, (address, port))
            response, server = sock.recvfrom(2048)

            if response and response[0] == 0x1C:
                return True
            else:
                return False
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            return False
        finally:
            sock.close()

def discord_alert(webhook_url, status):
    if status == True:
        payload = {"content": "Server is up!"}
    else:
        payload = {"content": "Server is down!"}
    
    requests.post(webhook_url, json=payload)

def log_status(status):
    if status == True:
        print('Server is up!')
    else:
        print('Server is down!')

def main():
    server_host = os.getenv("server_host")
    server_port = int(os.getenv("server_port"))
    healthcheck_interval = int(os.getenv("healthcheck_interval"))
    discord_webhook_url = os.getenv("discord_webhook_url")
    timeout = int(os.getenv("timeout"))
    max_retries = int(os.getenv("max_retries"))
    retry_delay = int(os.getenv("retry_delay"))
    
    past_status = True

    while True:
        current_status = send_raknet_ping(server_host, server_port, timeout, max_retries, retry_delay)

        if past_status != current_status:
            discord_alert(discord_webhook_url, current_status)
        
        past_status = current_status
        log_status(current_status)
        time.sleep(healthcheck_interval)

if __name__ == "__main__":
    main()
