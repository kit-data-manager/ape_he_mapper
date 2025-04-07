import argparse
import json
import logging
import os
import sys

from src.IO.MappingAbortionError import MappingAbortionError
from src.IO.InputReader import InputReader as InputReader_apeHe

# Make log level configurable from ENV, defaults to INFO level
logging.basicConfig(
    level=os.environ.get('LOGLEVEL', 'INFO').upper()
)

def get_args():
    parser = argparse.ArgumentParser(description='Extracting SEM FIB Tomography metadata to a unified json format')
    parser.add_argument('-i', '--input', help='Input zip file as file path', required=True)
    parser.add_argument('-m', '--map', help='Map file as path or remote URI', required=True)
    parser.add_argument('-o', '--output', help='Path to output json file', required=True)
    return parser.parse_args()

def run_cli():
    args = get_args() # Parse the arguments
    run_sem_mapper(args) # Run the SEM mapper with the parsed arguments

def run_sem_mapper(args):
    INPUT_SOURCE = args.input
    MAP_SOURCE = args.map
    OUTPUT_PATH = args.output

    try:
        reader = InputReader_apeHe(MAP_SOURCE, INPUT_SOURCE)
        #print("==========MAP_SOURCE:", MAP_SOURCE)
        #print("==========INPUT_SOURCE:", INPUT_SOURCE)

        img_info = reader.retrieve_image_info(INPUT_SOURCE)
        print("\n","==========IMAGE_INFO:", img_info)

        if not img_info:
            logging.error('Could not retrieve image information due to an unknown error. Aborting.')
            sys.exit(1)

        with open(OUTPUT_PATH, 'w', encoding="utf-8") as f:
            json.dump(img_info, f, indent=4, ensure_ascii=False)

    except MappingAbortionError as e:
        logging.error(f"Mapping abortion error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_cli()
