import logging
import os

from pydantic import BaseModel

from src.model.SchemaConcepts.APE_HE_Image import APE_HE_Image


class ImageMD(BaseModel):

    filePath: str
    image_metadata: APE_HE_Image = None

    def fileName(self):
        return os.path.basename(self.filePath)

    def folderName(self):
        return os.path.basename(os.path.dirname(self.filePath))