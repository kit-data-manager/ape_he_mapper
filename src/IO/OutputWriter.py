import json
import logging
from collections import defaultdict
from pprint import pprint
from typing import List

from pydantic import ValidationError

from src.IO.MappingAbortionError import MappingAbortionError
from src.model.ImageMD import ImageMD



class OutputWriter:

    """
    """