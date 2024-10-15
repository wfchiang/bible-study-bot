from typing_extensions import Unpack
from pydantic import BaseModel, ConfigDict
from typing import Dict, Union, List 


METADATA_TYPE = Dict[str, Union[str, int, float, List[str], List[int], List[float]]]


class TextChunk (BaseModel): 
    text :str 
    metadata :METADATA_TYPE


class BibleVerse (TextChunk): 
    pass 


class BibleBook (BaseModel): 
    name :str  
    metadata :METADATA_TYPE
    verses :List[BibleVerse]