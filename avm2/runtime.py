from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from avm2.abc.abc_types import ABCClassIndex

import BrewMaths as BM


@dataclass
class ASO_Seq:
    seq: ClassVar(int) = 0

@dataclass
class ASObject:
    #ASO_seq: ClassVar(int) = 0

    traceHint: str = '?!?'
    class_ix: Optional[ABCClassIndex] = None
    properties: Dict[Tuple[str, str], ASObject] = None # field(default_factory=dict)

    def __init__(self, traceHint: str, class_ix=None, properties=None):
      #if ASO_seq is None: ASO_seq = 0
      #self.ASO_seq   += 1
      ASO_Seq.seq +=1
      self.traceHint  = f'{traceHint}#{ASO_Seq.seq}' # self.ASO_seq}'
      self.class_ix   = class_ix
      if properties: self.properties = properties
      else: self.properties = dict()

@dataclass
class ASUndefined(ASObject):
    """
    pre-2023-11-30 printed as e.g.
Extra:-os.pop obj=ASUndefined(class_ix=None, properties={}).
	i.p:MEO:96: 	Extra:BTW #ER=4 SS#1 OS#0.
	i.p:MEO:96: 	Extra:BTW ER0=xyz.
	i.p:MEO:96: 	Extra:BTW ER1=ASUndefined(class_ix=None, properties={}).
	i.p:MEO:96: 	Extra:BTW ER2=ASUndefined(class_ix=None, properties={}).
	i.p:MEO:96: 	Extra:BTW ER3=ASUndefined(class_ix=None, properties={}).
    """
    def __init__(self, traceHint: str, class_ix=None, properties=None):
      super().__init__(traceHint, class_ix, properties)

undefined = ASUndefined(BM.LINE(False)) #
undefined2 = ASUndefined(BM.LINE(False)) #

@dataclass
class ASPrimitive(ASObject):
    value: Any = None
    def __init__(self, traceHint: str, value: Any):
      super().__init__(traceHint, class_ix=None, properties=None)
      self.value = value
