import os
import pytest

from mappingservice_plugincore.exceptions.MappingAbortionError import MappingAbortionError
from src.IO.InputReader import InputReader
from src.parser import ParserConfig
from src.parser.impl.NexusParser import NexusParser


class TestInputReader:

    def set_up_sample_data(self):
        dir_to_testscript = os.path.dirname(__file__)
        return os.path.join(dir_to_testscript, "../sampleData/")

    def test_get_applicable_nexusparser(self):
        tp = self.set_up_sample_data()
        test_file = os.path.join(tp, "IV_CURVE.nxs")
        ParserConfig.register_parsers()

        parsers = InputReader.get_applicable_parsers(test_file)
        assert len(parsers) >= 1

    def test_get_applicable_parsers_with_extension(self, mocker):
        tp = self.set_up_sample_data()
        nxs_file = os.path.join(tp, "2D_MAP_CELL.nxs")
        ParserConfig.register_parsers()

        # Patch the expected_input_format method to return the correct list
        #mocker.patch('src.parser.impl.NexusParser.NexusParser.expected_input_format', self.return_plaintext_format())
        mocker.patch.object(NexusParser, 'expected_input_format', return_value=["application/octet-stream", "application/x-hdf5"])

        assert "application/octet-stream" in NexusParser.expected_input_format()

        parsers = InputReader.get_applicable_parsers(nxs_file)
        assert len(parsers) >= 1

    def test_get_applicable_parsers_wo_extension(self, mocker):
        tp = self.set_up_sample_data()
        nxs_file = os.path.join(tp, "2D_MAP_CELL")
        ParserConfig.register_parsers()

        mocker.patch.object(NexusParser, 'expected_input_format', return_value=["application/octet-stream", "application/x-hdf5"])

        assert "application/octet-stream" in NexusParser.expected_input_format()

        parsers = InputReader.get_applicable_parsers(nxs_file)
        assert len(parsers) >= 1
