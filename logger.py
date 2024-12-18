import sys
from colorama import init, Fore, Style
import os

# Import readline for tab completion, check platform for cross compatibility
try:
    import readline  # Unix-like systems (Linux/macOS)
except ImportError:
    import pyreadline as readline  # Windows: fallback to pyreadline for tab completion


# Initialize colorama to support Windows and Linux
init(autoreset=True)

def printQuestion(message):
    """
    Desc: Prints a question formatted with a cyan color
    Args: 
        message (str): The question message to print
    Returns: None
    """
    print(f"{Fore.CYAN}[??]{Style.RESET_ALL} {message}")

def customPrompt(text):
    """
    Desc: prompts something to the user 
    Returns: a string containing the text typed by the user
    Args : none
    """

    printQuestion(text)
    prompt = input(f"Answ. > ")
    print()

    return prompt

def printInfo(message):
    """
    Desc: Prints an informational message formatted with a blue color
    Args: 
        message (str): The informational message to print
    Returns: None
    """
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")

def printError(message):
    """
    Desc: Prints an error message formatted with a red color
    Args: 
        message (str): The error message to print
    Returns: None
    """
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")

def printSuccess(message):
    """
    Desc: Prints a success message formatted with a green color
    Args: 
        message (str): The success message to print
    Returns: None
    """
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")
