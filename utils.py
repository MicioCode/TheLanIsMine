import os
from commands import *
import logger
from colorama import Fore, Style, Back

try:
    import readline
except ImportError:
    import pyreadline as readline  # for Windows

# debug
makeMeCrash = False

def welcomeUser():
    """
    Desc: prints the logo of the program and starts the shell
    Args: none
    Returns: none
    """

    print("""

        ,----,   ,--,                            
      ,/   .`|,---.'|                     ____   
    ,`   .'  :|   | :      ,---,        ,'  , `. 
  ;    ;     /:   : |   ,`--.' |     ,-+-,.' _ | 
.'___,/THE ,' |LAN' :   |   :  :  ,-+-. ;   , || 
|    :     |  ;   ; '   :   |  ' ,--.'|'   |  ;| 
;    |.';  ;  '   | |__ |   :  ||   |  ,', |  ': 
`----'  |  |  |   | :.'|'IS '  ;|   | /  | |  || 
    '   :  ;  '   :    ;|   |  |'   | :  | :  |, 
    |   |  '  |   |  ./ '   :  ;;   . |  ; |--'  
    '   :  |  ;   : ;   |   |  '|MI : |NE| ,     
    ;   |.'   |   ,/    '   :  ||   : '  |/      
    '---'     '---'     ;   |.' ;   | |`-'       
                        '---'   |   ;/           
                                '---'            
    """)

    startShell()

# This and quits() are the only commands in utils.py
# The other commands are in commands.py
def show_help():
    """
    Desc: shows the command list
    Args: none
    """

    logger.printInfo("Commands:")

    c = 0
    for command_name in command_map:
        print(f"- {Style.BRIGHT}{Fore.BLACK}{Back.WHITE}{command_name}{Style.RESET_ALL} {Style.DIM}| {Style.BRIGHT}{Fore.CYAN}{command_map[command_name][0]}{Style.RESET_ALL}")

        if c!=len(command_map)-1:
            print("")
        c+=1

def quits():
    """Stops the arpspoofing and quits the program"""
    import arpspoof
    arpspoof.shouldQuit = True
    logger.printSuccess("Bye")
    exit(1)


# Command List
command_map = {
    'help': 
    [
        "Shows the command list", 
        show_help
    ],
    'clear': 
    [
        "Clears the screen", 
        clear_screen
    ],
    'exit': 
    [
        "Exits the program", 
        quits
    ],
    'scan_devices': 
    [
        "Scans the local network for devices", 
        scan_network
    ],
    'list_devices': 
    [
        "Displays the list of found devices", 
        list_devices
    ],
    'list_targets': 
    [
        "Displays the list of current targets", 
        list_targets
    ],
    'add_target': 
    [
        "Adds a target to the target list", 
        add_target
    ],
    'remove_target': 
    [
        "Removes a target from the target list", 
        remove_target
    ],
    'start': 
    [
        "Starts the attack", 
        start_spoofing
    ],
    'stop': 
    [
        "Stops the attack", 
        stop_spoofing
    ]
}

# End of command list

def startShell():
    """
    Desc: gets a prompt from the user and processes the command
    Args: none
    """
    try:
        while True:
            p = prompt()
            processCommand(p) # send the string to the command manager
    except KeyboardInterrupt:
        logger.printError("CTRL-C detected")
        quits()

def processCommand(command):
    """
    Desc: processes the command submitted by the user
    Returns:
        0- command executed successfully
        1- command not found or bad syntax
        2- an exception occourred
    """

    cmd = command_map.get(command.lower()) # Commands are case-insensitive

    if cmd is not None: # Valid command
        command_func = cmd[1]  # Get the function associated with the command

        if not makeMeCrash:
            try:
                command_func()  # Call the desired function
            except Exception as e:
                logger.printError("An exception occourred.")
                print(e)
        else:
            command_func()

    else: # No command was found
        print("Unknown command. Type 'help' for a list of available commands.")

    print()


def getVersion():
    """
    Desc: returns the version of this program
    Args: none
    """
    return "v1.0"


def completer(text, state):
    """
    Completer function for tab completion.
    """

    command_list = [c for c in command_map]
 
    options = [cmd for cmd in command_list if cmd.startswith(text)]
    try:
        return options[state]
    except IndexError:
        return None

# Set the custom completer
readline.set_completer(completer)
readline.parse_and_bind("tab: complete")  # Bind tab key to invoke completion

def prompt():
    """
    Desc: prompts something to the user 
    Returns: a string containing the text typed by the user
    Args : none
    """

    prompt = input(f"TLIM {Style.DIM}{Fore.GREEN}{getVersion()}{Style.RESET_ALL} : @{Fore.GREEN}{arpspoof.get_gateway_ip()}{Style.RESET_ALL} > ")

    return prompt