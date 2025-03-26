import sys
from pathlib import Path
import toml

def configure_dll():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_dll>")
        sys.exit(1)

    dll_path = sys.argv[1]
    print(dll_path)