import argparse
import json
import logging
import os
import sys
import zipfile
import shutil
from pathlib import Path
from mappingservice_plugincore.file_util import is_zipfile
from mappingservice_plugincore.exceptions.MappingAbortionError import MappingAbortionError
from src.IO.InputReader import InputReader as InputReader_apeHe
from src.IO.OutputWriter import OutputWriter
from src.parser import ParserConfig

# Make log level configurable from ENV, defaults to INFO level
logging.basicConfig(
    level=os.environ.get('LOGLEVEL', 'INFO').upper()
)

def get_args():
    parser = argparse.ArgumentParser(description='Extracting APE-HE metadata to a json format')
    parser.add_argument('-i', '--input', help='Input file or zip file path', required=True)
    parser.add_argument('-m', '--map', help='Map file as path or remote URI', required=True)
    parser.add_argument('-o', '--output', help='Path to output json file', required=True)
    return parser.parse_args()

def run_cli():
    args = get_args()
    run_mapper(args)

def run_mapper(args):
    ParserConfig.register_parsers()
    INPUT_SOURCE = args.input
    MAP_SOURCE = args.map
    OUTPUT_PATH = args.output

    try:
        if is_zipfile(INPUT_SOURCE):
            temp_dir = os.path.splitext(INPUT_SOURCE)[0]
            logging.info(f"Extracting ZIP to temporary folder: {temp_dir}")
            extracted_files = []

            with zipfile.ZipFile(INPUT_SOURCE, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Collect all files (filter if needed, e.g., by extension)
            for file_path in Path(temp_dir).rglob("*"):
                if file_path.is_file() and "__MACOSX" not in str(file_path):
                    extracted_files.append(file_path)

            if not extracted_files:
                logging.error("No valid files found in zip archive. Aborting")
                sys.exit(1)

            list_of_file_names = []
            success_count = 0 # number of mapping that has been successful!

            for file in extracted_files:
                file_path = file.with_suffix('')
                logging.info(f"Processing extracted file: {file_path}")
                input_file = str(file)
                try:
                    result = process_input(input_file, MAP_SOURCE)
                    file_name = file_path.name + ".json"
                    OutputWriter.save_the_file(result, file_name)
                    list_of_file_names.append(file_name)
                    success_count += 1
                except MappingAbortionError as e:
                    logging.warning(f"Skipping file {input_file} due to mapping error: {e}")
                except Exception as e:
                    logging.exception(f"Unexpected error processing file {input_file}")

            if success_count > 0:
                logging.info(f"In total {success_count} file(s) were successfully processed.")
                OutputWriter.save_to_zip(list_of_file_names, OUTPUT_PATH)
                try:
                    shutil.rmtree(temp_dir)
                    logging.info(f"The temporary folder '{temp_dir}' has been deleted.")
                except Exception as e:
                    logging.error(f"Failed to delete temporary folder: {e}")
            else:
                logging.error("No files could be processed successfully. Aborting.")
                sys.exit(1)


        else:
            result = process_input(INPUT_SOURCE, MAP_SOURCE)
            OutputWriter.save_the_file(result, OUTPUT_PATH)


    except MappingAbortionError as e:
        logging.error(f"Mapping abortion error for {INPUT_SOURCE}: {e}")
        sys.exit(1)

def process_input(input_file, map_source):
    reader = InputReader_apeHe(map_source, input_file)
    img_info = reader.retrieve_image_info(input_file)
    logging.debug(f"IMAGE_INFO: {img_info}")

    if not img_info:
        raise MappingAbortionError(f"Could not retrieve image information for {input_file}.")

    return img_info

if __name__ == '__main__':
    run_cli()
