import subprocess
import getpass
import socket


def get_windows_user():
    """
    Helper function to get the windows user name
    Returns:
        (str)
    """
    return getpass.getuser()


def run_application_async(path):
    """
    Helper function to run Popen in a way that is more readable.
    Args:
        path: (str) Popen arg
    """
    subprocess.Popen(path)


def get_computer_name():
    """
    Helper function to get the local computer name
    Returns:
        (str) Name of the PC that ran this function.

    """
    return socket.gethostname()


def get_local_ip():
    """
    Helper function to get the local IP address of the computer.
    Returns:
        (str) IP address of the computer that ran this function.
    """
    return socket.gethostbyname(get_computer_name())
