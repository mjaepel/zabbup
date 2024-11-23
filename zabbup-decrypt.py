#!/bin/env python3
from modules.config import config
from modules.crypto import decrypt
from pydantic import ValidationError
import sys


def main():
    config.add_argument("-f", "--file", help="Input file to decrypt", required=True)
    try:
        config.load_data()
    except FileNotFoundError:
        print(f"Configuration file not found: {config.config_file}")
        sys.exit(1)
    except ValidationError as e:
        print(f"{e.error_count()} found in configuration file:")

        for error in e.errors():
            print(".".join(error["loc"]))
            print(f"    {error['msg']}")
        sys.exit(1)

    try:
        with open(config.args.file, 'rb') as f:
            data = f.read()
        print(decrypt(data, config.general.encryption_key))
    except Exception as e:
        print(f"Error on processing input file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
