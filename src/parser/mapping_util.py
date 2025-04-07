import logging
import re
import typing
import numpy as np
from jsonpath_ng.ext.parser import ExtentedJsonPathParser
from src.IO.MappingAbortionError import MappingAbortionError
import re

parser = ExtentedJsonPathParser()

def escape_pathelements(dotted_path):
    funct_match = re.search(r"`(.+?)`", dotted_path)
    if funct_match:
        function_name = funct_match.group(1)
        if function_name == "sorted":
            return dotted_path.replace(f"`{function_name}`", "FUNCTIONPLACEHOLDER")

    path_elements = dotted_path.split(".")
    escaped_elements = []
    for pe in path_elements:
        if not pe: 
            continue
        if "[" in pe:
            to_escape, to_keep = pe.split("[", 1)
            escaped = f"'{to_escape}'"
            pe = escaped + "[" + to_keep
        else:
            pe = f"'{pe}'"
        if pe == "'FUNCTIONPLACEHOLDER'":
            pe = "`sorted`"
        escaped_elements.append(pe)
    return ".".join(escaped_elements)

def flatten_dict(d, parent_key="", sep="."):
    flattened = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and v:
            flattened.update(flatten_dict(v, new_key, sep))
        else:
            flattened[new_key] = v
    return flattened

def extract_base_path(path: str):
    base_path = re.sub(r"\.`sorted`\[\d+\]$", "", path)  # Remove the sorted operation at the end
    sort_function = path.split('.')[-1]
    return base_path, sort_function


def apply_arithmetic(myArray):
    minValue = np.nanmin(myArray)
    maxValue = np.nanmax(myArray)
    avgValue = (minValue + maxValue) / 2.
    
    arithmetic = [round(el, 3) if not np.isnan(el) else el for el in [minValue, maxValue, avgValue]]

    arithmetic_dict = {'min_value': arithmetic[0], 'max_value': arithmetic[1], 'average_value': arithmetic[2]}
    return arithmetic_dict


def get_matching_keys(original_path_template,input_dict):
    # Check if the original_path_template contains (`*`)
    if '*' in original_path_template:
        # Extract the prefix (e.g., 'entry.sample.gas_flux_')
        prefix = original_path_template.split('*')[0]
        suffix = original_path_template.split('*')[-1]
        matching_keys = [k for k in flatten_dict(input_dict).keys() if k.startswith(prefix) and k.endswith(suffix)] # Find all keys in the original_dict that match the prefix
    else:
        matching_keys = [original_path_template]
    return matching_keys


# Function to create unified output dict based on the provided JSON mapping
def create_unified_dict(mapping, input_dict):
    output_dict = {}

    for k, v in mapping.items():

        k = escape_pathelements(k)
        # Firstly map the path_template(*) present in the map File with the correct key_paths
        if "*" in v:
            k_list = [escape_pathelements(el) for el in get_matching_keys(k,input_dict)]
            exprIN = [parser.parse(el) for el in k_list]
            values = []
            for el in exprIN:
                val = [m.value.item() if isinstance(m.value, np.ndarray) and len(m.value) == 1 else m.value for m in el.find(input_dict)]
                values.extend(val)
        else:
            exprIN = parser.parse(k)
            exprOUT = parser.parse(v)


        #print("<<<<<exprIN>>>>>>",exprIN)
        #print("<<<<<exprOUT>>>>>>",exprOUT)
        #print("<<>>",exprIN.find(input_dict))
        #values = [m.value for m in exprIN.find(input_dict)]
            values = [m.value.item() if isinstance(m.value, np.ndarray) and len(m.value) == 1 else m.value for m in exprIN.find(input_dict)]
        if not values:
            logging.warning("Mapping defined but no corresponding value found in input dict: {}".format(k))
            continue

        if not "*" in v: #as long as the output path in the map is not a list, we expect that we can map the input to one value
            #print("FALSE")
            try:
                if not all([isinstance(x, typing.Hashable) for x in values]):
                    #print("A-----> ",values)
                    logging.warning("Found multiple complex values in input dict, but output target is not a list. Only the first value will be used, no check for equivalence.")
                else:
                    assert len(set(values)) == 1
                    #print("B-----> ",values)
            except AssertionError:
                logging.error("Found multiple values in input dict, but output target is not a list. Aborting. Input path: {}, values: {}".format(k, values))
                raise MappingAbortionError("Mapping input to output format failed. Mapping not applicable.")
            try:
                if values[0]:
                    exprOUT.update_or_create(output_dict, values[0])
                else:
                    logging.warning("Found a value equivalent to None. path: {}, value: {}".format(k, values[0]))
            except Exception as e:
                logging.error("Unexpected error: {} at path: {}, values: {}".format(e, k, values))
        else: #split output in accordance to list of input values
            #print("TRUE")
            for i, value in enumerate(values):
                if value:
                    indexed_expr = parser.parse(v.replace('*', str(i)))
                    indexed_expr.update_or_create(output_dict, value)
                else:
                    logging.warning("Found a value equivalent to None. path: {}, value: {}".format(k, value))
    if not output_dict:
        logging.error("No output was produced by applying map to input. Was the correct mapping used?")
        raise MappingAbortionError("Mapping input to output format failed. Mapping not applicable.")
    return output_dict

def map_a_dict(input_dict, mapping_dict):
    return create_unified_dict(mapping_dict, input_dict)