import scapy.all as scapy
import time
import socket
import requests
import threading
from events import Events


class ScannerEvents(Events):
    __events__ = ('on_device_detected', 'on_all_devices_detected')


events = ScannerEvents()
threadRunner = True
whitelist = []


class ScannerThread(threading.Thread):
    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner

    def run(self):
        global threadRunner
        threadRunner = True
        while threadRunner:
            # Perform your desired operations in the infinite loop
            self.scanner.scan_network()
            print("Scanning...")
            time.sleep(5)

    def stop(self):
        global threadRunner
        threadRunner = False


class network_scanner():

    def __init__(self):
        # start
        self.mac_list = dict()
        self.should_scan_network = True
        self.t1 = threading.Thread()
        self.running = False
        self.data = ""
        self.approved_mac = {}
        self.ip = self.get_ip()
        # Define the range of IP addresses to scan - Will define the target IP in the file.
        self.ip_range = self.transform_ip_port(self.ip)
        self.scan_thread = None

    def get_company_name(self, mac_address):
        url = f"https://api.maclookup.app/v2/macs/{mac_address}/company/name"
        response = requests.get(url)

        if response.status_code == 200:
            company_name = response.content.decode('utf-8')
            return company_name
        else:
            return 'Unknown'

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53)) # 53 is the port of the DNS that belongs to Google.
        ip_addr = s.getsockname()[0]
        s.close()
        return ip_addr

    def transform_ip_port(self, ip):
        # Split the IP address by the dot separator
        ip_parts = ip.split('.')
        # Remove the last part of the IP address (x) and add '1/24' instead
        ip_parts[-1] = '1/24'
        # Join the IP address parts back together with dots
        transformed_ip = '.'.join(ip_parts)

        return transformed_ip

    def on_device_detected(self, ip, mac, source):
        global whitelist
        if mac in whitelist:
            return
        device = f"New device detected! IP: {ip}\t MAC: {mac}\t Company: {source}"
        self.data += f"{device}\n"
        whitelist.append(mac)
        events.on_device_detected(device)
        return device

    def on_all_devices_detected(self):
        events.on_all_devices_detected(self.data)
        self.data = ""

    def on_detected_device_updated(self, ip, mac, source):
        device = f"Update device: {ip}\tMAC: {mac} Company: {source}"
        self.data += f"{device}\n"
        events.on_device_detected(device)
        return device

    def scan_network(self):
        should_print = False

        # Create an ARP request packet to send to the broadcast MAC address
        arp_request = scapy.ARP(pdst=self.ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request

        # Send the packet and capture the responses
        answered, _ = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)

        # Check if the MAC address has already been seen before
        for packet in answered:
            mac_address = packet[1].hwsrc
            if mac_address not in self.approved_mac:
                if mac_address not in self.mac_list:
                    company_name = self.get_company_name(mac_address)
                    self.mac_list[mac_address] = company_name
                    data_to_print = self.on_device_detected(packet[1].psrc, mac_address, company_name)
                    if data_to_print is not None:
                        print(data_to_print)
                        should_print = True
                else:
                    if self.mac_list[mac_address] == 'Unknown':
                        company_name = self.get_company_name(mac_address)
                        self.mac_list[mac_address] = company_name
                        print(self.on_detected_device_updated(packet[1].psrc, mac_address, company_name))
                        should_print = True

        if should_print:
            self.data = self.data.rstrip('\n')
            self.on_all_devices_detected()

    def start_network_scanning(self):
        if self.scan_thread is None or not self.scan_thread.is_alive():
            self.scan_thread = ScannerThread(self)  # Create a new instance of ScannerThread
            self.scan_thread.start()

    def stop_network_scanning(self):
        if self.scan_thread is not None and self.scan_thread.is_alive():
            self.scan_thread.stop()
            self.scan_thread = None

    def wait_for_completion(self):
        if self.scan_thread is not None and self.scan_thread.is_alive():
            self.scan_thread.join()
