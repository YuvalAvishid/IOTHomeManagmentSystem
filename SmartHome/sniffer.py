import scapy.all as scapy
import time
import socket
import requests

mac_list = dict()

def get_company_name(mac_address):
    url = f"https://api.maclookup.app/v2/macs/{mac_address}/company/name"
    response = requests.get(url)

    if response.status_code == 200:
        company_name = response.content.decode('utf-8')
        return company_name
    else:
        return 'Unknown'

def get_ip():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    return IPAddr

def transform_ip_port(ip):
    # Split the IP address by the dot separator
    ip_parts = ip.split('.')
    # Remove the last part of the IP address (x) and add '1/24' instead
    ip_parts[-1] = '1/24'
    # Join the IP address parts back together with dots
    transformed_ip = '.'.join(ip_parts)

    return transformed_ip

def scan_network():
    ip = get_ip()
    ip_r = transform_ip_port(ip)
    # Define the range of IP addresses to scan - Will define the target IP in the file.
    ip_range = ip_r

    # Create an ARP request packet to send to the broadcast MAC address
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    # Send the packet and capture the responses
    answered, _ = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)

    # Check if the MAC address has already been seen before
    for packet in answered:
        mac_address = packet[1].hwsrc
        if mac_address not in mac_list:
            company_name = get_company_name(mac_address)
            mac_list[mac_address] = company_name
            print(f"New device detected! IP: {packet[1].psrc}\tMAC: {mac_address} Company: {company_name}")
        else:
            if mac_list[mac_address] == 'Unknown':
                company_name = get_company_name(mac_address)
                mac_list[mac_address] = company_name
                print(f"Update device: {packet[1].psrc}\tMAC: {mac_address} Company: {company_name}")

if __name__ == '__main__':
    while True:
        scan_network()
        time.sleep(10)  # wait 10 seconds before scanning again