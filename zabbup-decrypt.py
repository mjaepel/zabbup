#!/bin/env python3
from pydantic import ValidationError
import sys

try:
    from modules.logger import GetLogger
    from modules.config import config
    from modules.crypto import decrypt
except ValidationError as e:
    print(f"{e.error_count()} found in configuration file:")

    for error in e.errors():
        print(".".join(error["loc"]))
        print(f"    {error['msg']}")
    sys.exit(1)



def main():
    file = sys.argv[1]
    with open(file, 'rb') as f:
        data = f.read()
    print(decrypt(data, config.general.encryption_key))



if __name__ == "__main__":
    main()
