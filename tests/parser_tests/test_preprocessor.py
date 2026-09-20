import importlib
import inspect
from enum import Enum
import re

from src.Preprocessor import Preprocessor


class TestPreprocessor:

    def test_unit_replacement(self):
        input_dict = {
            "some": {
                "nested": {
                    "units": [
                        {"unit": "\udcb0"},
                        {"unit": "\udcb0C"},
                    ]
                }
            }
        }

        units_module = importlib.import_module('src.model.SchemaConcepts.codegen.SchemaClasses_APE_HE')

        # Collect all unit values that are allowed
        all_units = set()

        # Pattern to find names like Unit1, Unit2, ...
        unit_class_pattern = re.compile(r'^Unit\d+$')
        for name, cls in inspect.getmembers(units_module, inspect.isclass):
            if unit_class_pattern.match(name) and issubclass(cls, Enum) and cls.__module__ == units_module.__name__:
                for unit in cls:
                    all_units.add(unit.value)

        Preprocessor.normalize_all_units(input_dict)
        print(all_units)
        normalized_units = [x["unit"] for x in input_dict['some']['nested']['units']]
        print(normalized_units)
        assert not [x for x in normalized_units if x not in all_units]

    def test_normalize_gas_name(self): # TODO
        input_dict = {
            "somePath": {
                "nested": {
                    "gas_name": [
                        {"name": "/path/to/gas_flux_C2H4"},
                        {"name": "/path/to/gas_flux_N2"},
                    ]
                }
            }
        }


    def test_normalize_all_numbers(self): #TODO
        input_dict = {
            "somePath": {
                "nested": {
                    "gas_name": [
                        {"value": "25.3"},
                        {"value": "273"},
                    ]
                }
            }
        }

    def test_get_expected_type(self):
        # Simple field path
        assert Preprocessor.get_expected_type(
            "entry.entry_identifier"
        ) == "string_type"

        # Path containing parentheses
        assert Preprocessor.get_expected_type(
            "(((((entry.instrument).monochromator).grating).period).value)"
        ) == "int_type"

        # Path containing parentheses and a list index
        assert Preprocessor.get_expected_type(
            "((((entry.sample).gas_flux).[0]).value)"
        ) == "float_type"

        # Unknown field
        assert Preprocessor.get_expected_type(
            "entry.unknown.field"
        ) is None

