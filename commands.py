import os
from TILMnetworkingUtils import *
import logger
import arpspoof
import TILMnetworkingUtils

nonDeviceType = "Why is there a non-device type here?!?!"

# Global variables to hold discovered and target devices
discovered_devices = []
target_devices = []

def clear_screen():
    """
    Desc: Clears the screen in the terminal, works on Windows, Linux, and macOS.
    Args: none
    Returns: none
    """
    if os.name == 'nt':  # For Windows
        os.system('cls')  # Clear screen for Windows
    else:  
        os.system('clear')


def checkDevices():
    """
    Desc: Checks if any devices have been discovered.
    Args: none
    Returns: 
        bool: Returns False if no devices are found, otherwise True.
    """
    if discovered_devices == []:
        logger.printError("No devices found. Try 'scan'")
        return False
    return True

def checkTargets():
    """
    Desc: Checks if any targets have been added.
    Args: none
    Returns: 
        bool: Returns False if no targets are found, otherwise True.
    """
    if target_devices == []:
        logger.printError("No targets found. Try adding one")
        return False
    return True

def list_devices():
    """
    Desc: Lists all discovered devices with their IP, MAC, and hostname.
    Args: none
    Returns: none
    """
    global discovered_devices

    if not checkDevices():
        return

    index = 0
    logger.printSuccess("Listing devices...")  

    for device in discovered_devices:
        try:
            ip = device.getIp()  # Get the IP address of the device
            hostname = device.getHostname()  # Get the hostname of the device
            mac = device.getMac()  # Get the MAC address of the device
        
            logger.printInfo(f"{Fore.YELLOW}{index}{Style.RESET_ALL}] {Fore.GREEN}{ip}{Style.RESET_ALL} || {Fore.GREEN}{mac}{Style.RESET_ALL} || ({Fore.GREEN}{hostname}{Style.RESET_ALL})")
            index += 1
        
        except AttributeError:
            logger.printError(nonDeviceType)
            pass

def add_target():
    """
    Desc: Adds a target device to the target devices list.
    Args: none
    Returns: none
    """
    global target_devices
    global discovered_devices

    if not checkDevices():
        return

    _id_ = logger.customPrompt("Enter device ID:")

    desired_device = discovered_devices[int(_id_)]

    try:
        ip = desired_device.getIp()
        mac = desired_device.getMac()
        hostname = desired_device.getHostname()
    except AttributeError:
        logger.printError(nonDeviceType)
        return

    target_devices.append( Device(ip, mac, hostname) )

    logger.printSuccess(f"Succesfully added {Fore.RED}{ip}{Style.RESET_ALL} || {Fore.RED}{mac}{Style.RESET_ALL} || ({Fore.RED}{hostname}{Style.RESET_ALL}) to the target list")

def start_spoofing():
    """
    Desc: Starts the arp spoofing attack
    Args: none
    """
    arpspoof.run = True
    logger.printSuccess("Started spoofing")
    

def stop_spoofing():
    """
    Desc: Stops the arp spoofing attack
    Args: none
    """
    arpspoof.run = False
    logger.printSuccess("Stopped spoofing")
    TILMnetworkingUtils.restore_arp_table()
    logger.printSuccess("Restored the arp table")


def remove_target():
    """
    Desc: Removes a target device from the target devices list.
    Args: none
    Returns: none
    """
    global target_devices

    if not checkTargets():
        return

    _id_ = logger.customPrompt("Enter device ID:")

    desired_device = target_devices[int(_id_)]

    target_devices.remove(desired_device)

    logger.printSuccess(f"Removed target n.{Fore.RED}{_id_}{Style.RESET_ALL} from the target list")

def list_targets():
    """
    Desc: Lists all added target devices with their IP, MAC, and hostname.
    Args: none
    Returns: none
    """
    global target_devices

    if not checkTargets():
        return

    index = 0
    logger.printSuccess("Listing targets...")

    for device in target_devices:
        try:
            ip = device.getIp()  # Get the IP address of the target device
            hostname = device.getHostname()  # Get the hostname of the target device
            mac = device.getMac()  # Get the MAC address of the target device
        
            logger.printInfo(f"{Fore.YELLOW}{index}{Style.RESET_ALL}] {Fore.RED}{ip}{Style.RESET_ALL} || {Fore.RED}{mac}{Style.RESET_ALL} || ({Fore.RED}{hostname}{Style.RESET_ALL})")
            index += 1
        
        except AttributeError:
            logger.printError(nonDeviceType)
            pass

def scan_network():
    """
    Desc: Scans the network and prints the devices that are found.
    Args: none
    Returns: none
    """
    global discovered_devices
    discovered_devices = [] # Reset the discovered list every time we run this command

    discovered_devices = discover()  
