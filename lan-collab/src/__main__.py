# Contents of /lan-collab/lan-collab/src/__main__.py

import sys
from app import start_application

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m lan-collab [server|client]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == 'server':
        start_application(mode)
    elif mode == 'client':
        start_application(mode)
    else:
        print("Invalid mode. Please choose 'server' or 'client'.")
        sys.exit(1)

if __name__ == "__main__":
    main()