import socket
import time
import threading

UDP_PORT = 4444
MY_SERVER_IP = "172.27.224.1"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("0.0.0.0", UDP_PORT))

found_devices = {}


def listen_for_devices():
    print("Dashboard listening for Loggers...")
    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8', errors='ignore')

        if message.startswith("LOGGER_BEACON:"):
            mac_address = message.split(":")[1]
            if mac_address not in found_devices:
                print(f"\n[NEW DEVICE FOUND] MAC: {mac_address} at IP: {addr[0]}")
                found_devices[mac_address] = addr[0]

        elif len(data) == 114:
            pass

listener_thread = threading.Thread(target=listen_for_devices)
listener_thread.daemon = True
listener_thread.start()

while True:
    cmd = input("\nType 'list' to see devices, or 'connect [MAC]' to configure: ")

    if cmd == "list":
        print("--- DISCOVERED LOGGERS ---")
        for mac, ip in found_devices.items():
            print(f"Device: {mac} | IP: {ip}")

    elif cmd.startswith("connect"):
        try:
            target_mac = cmd.split(" ")[1]
            if target_mac in found_devices:
                target_ip = found_devices[target_mac]

                msg = f"CONFIG_SET_IP:{MY_SERVER_IP}"
                sock.sendto(msg.encode(), (target_ip, UDP_PORT))

                print(f"Sent Configuration to {target_mac}. It should start streaming now.")
            else:
                print("MAC address not found in list.")
        except:
            print("Invalid command. Usage: connect AA:BB:CC:DD:EE:FF")
