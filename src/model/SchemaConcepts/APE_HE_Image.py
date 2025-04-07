from pydantic import BaseModel

from src.model.SchemaConcepts.Schema_Concept import Schema_Concept
from src.model.SchemaConcepts.codegen.SchemaClasses_APE_HE import Entry, ApeHe


class APE_HE_Image(Schema_Concept, BaseModel):

    entry: Entry = None

    def as_schema_class(self):
        return ApeHe(**self.model_dump())