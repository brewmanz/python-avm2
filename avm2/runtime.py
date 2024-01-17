from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from avm2.abc.abc_types import ABCClassIndex

import BrewMaths as BM

def ValueIsNull(value) -> bool:
  '''
  >>> ValueIsNull(None)
  True
  >>> ValueIsNull(undefined)
  False
  >>> ValueIsNull(123)
  False
  >>> ValueIsNull(123.45)
  False
  >>> ValueIsNull('')
  False
  >>> ValueIsNull('a')
  False
  '''
  if value == None: return True
  return False

def ValueIsNullOrUndefined(value) -> bool:
  '''
  >>> ValueIsNullOrUndefined(None)
  True
  >>> ValueIsNullOrUndefined(undefined)
  True
  >>> ValueIsNullOrUndefined(123)
  False
  >>> ValueIsNullOrUndefined(123.45)
  False
  >>> ValueIsNullOrUndefined('')
  False
  >>> ValueIsNullOrUndefined('a')
  False
  '''
  if value == None: return True
  if isinstance(value, ASUndefined): return True
  return False


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

if __name__ == '__main__':  # 2024-01-17 # when you run 'python thisModuleName.py' ...
  import doctest, os, sys
  # vvvv use BM.LINE() in other modules (after 'import BrewMaths as BM')
  print(f'@{BM.LINE()} ### run embedded unit tests via \'python ' + os.path.basename(__file__) + '\'')
  if False and True: # 'and' = not verbose; 'or' = verbose
    res = doctest.testmod(verbose=True) # then the tests in block comments will run. nb or testmod(verbose=True)
  else:
    res = doctest.testmod() # then the tests in block comments will run. nb or testmod(verbose=True)
  emoji = '\u263a \U0001f60a' if res.failed == 0 else '\u2639 \U0001f534'  # smile+happy else sad+red
  print(f'@{BM.LINE()} ### BTW res = <{res}>, res.failed=<{res.failed}> {"!"*res.failed} {emoji}')
  sys.exit(res.failed) # return number of failed tests
