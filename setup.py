import sys
from core.setup import setup as setup_win32

def setup():
    if sys.platform == "win32":
        print("Setting up on windows..")
        setup_win32()
    else:
        print("This program only supported in Windows")

if __name__ == "__main__":
    setup()