from flask._compat import text_type
from flask.json import JSONEncoder as BaseEncoder
from speaklater import _LazyString


class JSON_Encoder(BaseEncoder):
   """Custom serializer to serialize lazystring"""

   def default(self, o):
       if isinstance(o, _LazyString):
           return text_type(o)

       return BaseEncoder.default(self, o)