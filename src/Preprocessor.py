import logging
from typing import Any

import numpy as np
from jsonpath_ng.parser import JsonPathParser
from mappingservice_plugincore.Preprocessor import Preprocessor as CorePreprocessor


class Preprocessor(CorePreprocessor):
    """
    APE-HE-specific preprocessing before schema construction.

    The core preprocessor already handles generic datetime normalization.
    This subclass keeps only APE-HE / NeXus-specific behavior:
    - schema-specific unit normalization
    - numeric string conversion
    - NumPy array value conversion
    - gas name extraction from NeXus-style paths
    """

    parser = JsonPathParser()

    unit_normalization = {
        "deg": "degrees",
        "degr": "degrees",
        "°": "degrees",
        "\udcb0": "degrees",
        "\udcb0C": "°C",
        "Secs": "s",
        "Mins": "min",
    }

    expected_types = {
        "entry.entry_identifier": "string_type",
        "entry.title": "string_type",
        "entry.sample.gas_flux[*].value": "float_type",
    }

    @classmethod
    def get_expected_type(cls, field_path: str):
        exact_match = cls.expected_types.get(field_path)
        if exact_match:
            return exact_match

        for pattern, expected_type in cls.expected_types.items():
            if pattern in field_path:
                return expected_type

        return None

    @staticmethod
    def is_numeric_string(value: Any) -> bool:
        if not isinstance(value, str):
            return False

        try:
            float(value)
            return True
        except ValueError:
            return False

    @classmethod
    def convert_numeric_string(cls, value: Any):
        if not cls.is_numeric_string(value):
            return value

        try:
            if "." not in value and "e" not in value.lower():
                return int(value)
            return float(value)
        except ValueError:
            return value

    @classmethod
    def normalize_unit(cls, input_value) -> str:
        return cls.unit_normalization.get(input_value, input_value)

    @classmethod
    def normalize_all_units(cls, input_dict):
        unit_fields = cls.parser.parse("$..unit")

        for match in unit_fields.find(input_dict):
            if not isinstance(match.value, str):
                continue

            normalized_value = cls.normalize_unit(match.value)
            if normalized_value != match.value:
                match.full_path.update(input_dict, normalized_value)

    @classmethod
    def normalize_number_value(cls, value, expected_type=None):
        if isinstance(value, str):
            if expected_type == "string_type":
                return value
            if expected_type == "int_type":
                return int(value)
            if expected_type == "float_type":
                return float(value)
            return cls.convert_numeric_string(value)

        return value

    @classmethod
    def normalize_numpy_array(cls, value):
        if not isinstance(value, np.ndarray) or value.size == 0:
            return value

        try:
            return value.astype(float)
        except (TypeError, ValueError):
            logging.warning("Could not convert NumPy array values to float: %s", value)
            return value

    @classmethod
    def normalize_all_numbers(cls, input_dict):
        number_fields = cls.parser.parse("$..*")

        for match in number_fields.find(input_dict):
            original_value = match.value
            current_field = str(match.full_path)
            expected_type = cls.get_expected_type(current_field)

            try:
                if isinstance(original_value, str):
                    converted_value = cls.normalize_number_value(original_value, expected_type)
                    if converted_value != original_value:
                        match.full_path.update(input_dict, converted_value)

                elif isinstance(original_value, np.ndarray):
                    converted_value = cls.normalize_numpy_array(original_value)
                    if converted_value is not original_value:
                        match.full_path.update(input_dict, converted_value)

            except ValueError:
                logging.warning(
                    "Error while trying to convert '%s' into %s for field %s",
                    original_value,
                    expected_type,
                    current_field,
                )

    @classmethod
    def normalize_gas_names(cls, input_dict):
        gas_fields = cls.parser.parse("$..gas_name")

        for match in gas_fields.find(input_dict):
            original_value = match.value

            if isinstance(original_value, str) and "/" in original_value:
                possible_gas = original_value.split("_")[-1]
                match.full_path.update(input_dict, possible_gas)
            else:
                logging.warning("Unexpected gas name format: %s", original_value)