import socket
import threading
from datetime import datetime

UDP_PORT = 4444


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


MY_SERVER_IP = get_local_ip()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("0.0.0.0", UDP_PORT))

provisioned_devices = set()  # Track IDs that we have already configured

print(f"--- Server Started on {MY_SERVER_IP} ---")
print("Listening for Loggers and auto-configuring new devices...\n")


def handle_incoming_packets():
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8', errors='ignore')
            client_ip = addr[0]

            if message.startswith("LOGGER_BEACON:"):
                device_id = message.split(":")[1]

                if device_id not in provisioned_devices:
                    print(f"[NEW DEVICE] Found {device_id} at {client_ip}. Sending config...")

                    config_msg = f"CONFIG_SET_IP:{MY_SERVER_IP}"
                    sock.sendto(config_msg.encode(), (client_ip, UDP_PORT))

                    provisioned_devices.add(device_id)
                else:
                    pass

            elif "val" in message:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] DATA from {client_ip}: {message}")

        except Exception as e:
            print(f"Error processing packet: {e}")


listener_thread = threading.Thread(target=handle_incoming_packets, daemon=True)
listener_thread.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nShutting down server...")
    sock.close()
