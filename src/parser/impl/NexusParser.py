import logging
from typing import Optional

from PIL import Image

from src.Preprocessor import Preprocessor
from src.model.ImageMD import ImageMD
from src.parser.ImageParser import ImageParser
from src.parser.mapping_util import map_a_dict
from src.resources.maps.mapping import nexusparser_apeHe
from src.util import input_to_dict
import configparser



class NexusParser(ImageParser):

    internal_mapping = None
    expected_input = "application/octet-stream"

    def __init__(self):
        m = input_to_dict(nexusparser_apeHe.read_text())
        self.internal_mapping = m

    @staticmethod
    def expected_input_format():
        return "application/octet-stream"

    def parse(self, file_path, mapping) -> tuple[ImageMD, str]:
        input_md = self._read_input_file(file_path)

        if not input_md:
            logging.warning("No metadata extractable from {}".format(file_path))
            return None, None

        if not mapping and not self.internal_mapping:
            logging.error("No mapping provided for image parsing. Aborting")
            exit(1)
        mapping_dict = mapping if mapping else self.internal_mapping
        image_md = map_a_dict(input_md, mapping_dict)

        #Preprocessor.normalize_all_datetimes(image_md)
        Preprocessor.normalize_all_numbers(image_md)
        Preprocessor.normalize_all_units(image_md)
        Preprocessor.normalize_gas_names(image_md)

        image_from_md = ImageMD(image_metadata=image_md, filePath="")

        return image_from_md, image_md

    def _read_input_file(self, file_path) -> Optional[dict]:
        """
        Reading input may be done with a predefined tag or without. In the latter case we try to extract from all tags and use the joint dictionary for mapping.
        :param file_path: image file path
        :param tagID: tag to extract from, may be None
        :return: data from extracted tag(s) as dict
        """

        # Read the .nxs file
        md = file_path

        output_dict = {}
        parsed_dict = input_to_dict(md)

        if parsed_dict is None:
            logging.error(f"Not able to parse {md}.")
            return None

        output_dict.update(parsed_dict)
        return output_dict
