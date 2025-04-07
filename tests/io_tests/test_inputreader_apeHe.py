import os

import pytest

from src.IO.InputReader import InputReader
from src.parser.impl.NexusParser import NexusParser


class TestInputReader:

    def set_up_sample_data(self):
        dir_to_testscript = os.path.split(__file__)[0]

        test_path = os.path.join(dir_to_testscript, "../sampleData/")
        return test_path

    def return_plaintext_format(self):
        return "application/octet-stream"

    def test_get_applicable_nexusparser(self, mocker):
        tp = self.set_up_sample_data()

        tffile = os.path.join(tp, "IV_CURVE.nxs")

        parsers = InputReader.get_applicable_parsers(tffile)
        assert len(parsers) >= 1

        tffile = os.path.join(tp, "IV_CURVE.nxs")

        parsers = InputReader.get_applicable_parsers(tffile)
        assert len(parsers) >= 1

    def test_get_applicable_parsers_with_extension(self, mocker):
        tp = self.set_up_sample_data()

        ret = "application/octet-stream"
        mocker.patch('src.parser.impl.NexusParser.NexusParser.expected_input', self.return_plaintext_format())
        assert NexusParser.expected_input_format() == "application/octet-stream"

        nxsfile = os.path.join(tp, "2D_MAP_CELL.nxs")

        parsers = InputReader.get_applicable_parsers(nxsfile)
        assert len(parsers) >= 1

    def test_get_applicable_parsers_wo_extension(self, mocker):
        tp = self.set_up_sample_data()

        ret = "application/octet-stream"
        mocker.patch('src.parser.impl.NexusParser.NexusParser.expected_input', self.return_plaintext_format())
        assert NexusParser.expected_input_format() == "application/octet-stream"

        nxsfile = os.path.join(tp, "2D_MAP_CELL.nxs")

        parsers = InputReader.get_applicable_parsers(nxsfile)
        assert len(parsers) >= 1
