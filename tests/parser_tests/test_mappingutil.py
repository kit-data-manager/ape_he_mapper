import pytest
import numpy as np
import jsonpath_ng.ext
from src.parser.mapping_util import escape_pathelements, apply_arithmetic, get_matching_keys, create_unified_dict
from mappingservice_plugincore.exceptions.MappingAbortionError import MappingAbortionError


class TestMappingUtil:

    def test_escape_dottedpaths(self):
        """
        The test mainly checks for expected usages of functions and unexpected tokens in dotted path.
        In case of extension in functionality of the parsing, this test may need adaption to more test inputs
        :return:
        """
        inputpaths = [
            "some.path.to.list[*]",
            "some.#path.to.list[*]",
            "some.path.to.#list[*]",
            "some.path.to.list[3].`sub(/.*/, replacement)`",
            "some.path.to`split(\",\", *, -1)`",
            "some.path.to.`arithmetic`[-1]"
        ]

        vallist = [1,2,3, "some string"]

        match_dict = {
            "some": {
                "path": {
                    "to": {
                        "list": vallist,
                        "#list": vallist
                    }
                },
                "#path": {
                    "to": {
                        "list": vallist,
                        "#list": vallist
                    }
                }
            }
        }

        for ip in inputpaths:
            escaped = escape_pathelements(ip)
            p = jsonpath_ng.ext.parse(escaped) #if this succeeds, the escaped version does not throw an error about unexpected characters
            values = [m.value for m in p.find(match_dict)]
            if not "`" in ip: #bit harder to check dummy functions, so we are satisfied with getting any result
                assert len(values) == len(vallist)

    def test_apply_arithmetic_values(self):
        result = apply_arithmetic([1, 2, np.nan, 3])
        assert result == {'min_value': 1.0, 'max_value': 3.0, 'avg_value': 2.0}

    def test_get_matching_keys_with(self):
        data = {"entry": {"sample": {"gas_flux_a": 1, "gas_flux_b": 2}}}
        keys = get_matching_keys("entry.sample.gas_flux_*", data)
        assert set(keys) == {"entry.sample.gas_flux_a", "entry.sample.gas_flux_b"}

    def test_create_unified_dict_gas_flux(self):
        input_data = {
            "somePath": {
                "gas_flux_C2H4": {
                    "name": "/path/to/gas_flux_C2H4",
                    "value": "25.3",
                    "unit": "ml/min"
                },
                "gas_flux_N2": {
                    "name": "/path/to/gas_flux_N2",
                    "value": "273",
                    "unit": "ml/min"
                }
            }
        }
        
        mapping = {"somePath.gas_flux_*.name": "somePath.gas_flux[*].gas_name",
                   "somePath.gas_flux_*.value": "somePath.gas_flux[*].value",
                   "somePath.gas_flux_*.unit": "somePath.gas_flux[*].unit"}
        
        output = create_unified_dict(mapping, input_data)
        assert output == {"somePath":{"gas_flux": [{"gas_name": '/path/to/gas_flux_C2H4', "value": "25.3", "unit": "ml/min"}, {"gas_name": "/path/to/gas_flux_N2", "value": "273", "unit": "ml/min"}]}}