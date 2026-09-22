import enum
from typing import Type

from mappingservice_plugincore.parser.ParserFactory import ParserFactory
from mappingservice_plugincore.parser.RunMD_Parser import RunMD_Parser
from src.parser.impl.NexusParser import NexusParser


available_img_parsers = {
    "NexusParser": NexusParser
}

def register_parsers():

    for p_name, p_cls in available_img_parsers.items():
        ParserFactory.register_imgparser(p_name, p_cls)