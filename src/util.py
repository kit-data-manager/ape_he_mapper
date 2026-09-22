import json
import logging
from pathlib import Path

import h5py

from magika import Magika
import os
import tempfile
import time
from json import JSONDecodeError
from typing import Optional
import configparser
import numpy as np

import requests
import zipfile

from mappingservice_plugincore.exceptions.MappingAbortionError import MappingAbortionError
from mappingservice_plugincore.file_util import get_filetype_with_magica
def _import_nxs_as_dict(obj, group=''):
    """
    Recursive function to travel all over the Nexus file tree and extract all data and metadata as a dictionary.
    Inputs:
        obj: h5py (object)
    Output:
        inputFile (dictionary)
    """
    inputFile = {}

    if isinstance(obj, h5py.Group):
        for key in obj.keys(): # Iterate through all items in the group
            full_directory = f"{group}.{key.strip()}" if group else key
            inputFile.update(_import_nxs_as_dict(obj[key], full_directory))
    elif isinstance(obj, h5py.Dataset):
        try:
            # Get dataset information
            dataset_info = {
                'name': obj.name,
                'attributes': dict(obj.attrs)  # Attributes of the dataset
            }

            # Extract the contents of the dataset (Handle scalar and array datasets)
            if isinstance(obj[()], np.ndarray):
                dataset_info['value'] = obj[()]
            else:
                dataset_info['value'] = obj[()].decode('utf-8')

            inputFile[group] = dataset_info # Add dataset info to the main dictionary
        except Exception as e:
            logging.warning(f"Error processing dataset {group}: {e}")
    return {key.replace('/', '.'): value for key, value in inputFile.items()}


def _flat_to_nested_dict(flat_dict):
    nested_dict = {}
    
    for flat_key, value in flat_dict.items():
        keys = flat_key.split('.') # Split the key by dots
        current_level = nested_dict

        for key in keys[:-1]:
            if key not in current_level:
                current_level[key] = {}
            current_level = current_level[key]
        
        current_level[keys[-1]] = value # Assign the value to the last key
    
    return nested_dict

def input_to_dict(stringPayload) -> Optional[dict]:
    if type(stringPayload) is not str:
        return None
    #print("--------im trying--------------", stringPayload)
    try:
        #print("----->", get_filetype_with_magica(stringPayload))
        if stringPayload.startswith("{"):
            try: #JSON
                logging.info("Reading json file was successful!")
                return json.loads(stringPayload)
            except JSONDecodeError:
                logging.debug("Reading input as json not successful")
        if get_filetype_with_magica(stringPayload) in ["application/octet-stream", "application/x-hdf5"]:
            try: #NXS
                with h5py.File(stringPayload, 'r') as f:
                    logging.info("Reading neXus/hdf5 file was successful!")
                    return _flat_to_nested_dict(_import_nxs_as_dict(f))
            except Exception as e:
                logging.debug(f"Error reading Nexus/hdf5 file: {e}")
    except Exception as e:
        logging.warning("Best effort input reading failed with unexpected error. Input malformed?")
        logging.error(e)
