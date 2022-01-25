from os import name
from re import A
from typing import Optional, Union, Iterable, List, Dict, BinaryIO
from SimilarNeuron import BaseSwitch, Agreement
from ..internaltype import (
    MessageChain,
    At,
    Source,
    AtAll,
    Image,
    Face,
    Plain,
    FlashImage,
    Voice
)

class DictToMessageChain(BaseSwitch):
    external: Dict[str, Union[str, bytes, BinaryIO]]
    internal: MessageChain

    @classmethod
    def transform(cls, external: Dict[str, Union[str, bytes, BinaryIO]]) -> str:
        def mulel(v):
            # if isinstance(v, str):
            #     return {'url': v}
            # elif isinstance(v, (bytes, BinaryIO)):
            #     return {'data_bytes': v}
            # raise TypeError(f'{v} is not a valid type')
            return {'data_bytes': v}

        def to_form():
            for k,v in external.items():
                if k == 'Plain':
                    yield Plain(v)
                elif k == 'At':
                    yield At(target = v)
                elif k == 'Image':
                    yield Image(**mulel(v))
                elif k == 'Face':
                    yield Face(name = k)
                elif k == 'FlashImage':
                    yield FlashImage(**mulel(v))
                elif k == 'Voice':
                    yield Voice(**mulel(v))
                elif k == 'AtAll':
                    yield AtAll()
        
        return MessageChain.create(to_form())