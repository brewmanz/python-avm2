from __future__ import annotations

from dataclasses import dataclass, field, fields
import sys
from typing import Any, Callable, ClassVar, Dict, Tuple, Type, TypeVar, NewType, Optional

import BrewMaths as BM

import avm2.vm
from avm2.exceptions import ASReturnException, ASJumpException
from avm2.runtime import undefined, ASPrimitive
from avm2.abc.abc_parser import read_array
from avm2.io import MemoryViewReader
from avm2.abc.abc_enums import MultinameKind
import avm2.runtime as RT

import inspect
import logging

# to run doctest, go up a few levels and use 'python avm2/abc/abc_instructions.py'
strBACKWARDS_n = 'BACKWARDS\n'

@dataclass
class bagForFindingInternalMethod:
  """
  >>> myObj = 'abcdef'
  >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
  >>> myMethod = 'charAt'
  >>> myArgs = list()
  >>> myArgs.append(1)
  >>> myArgs.append(2.0)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs)
  >>> bag
  bagForFindingInternalMethod(instance='abcdef', namespaceName='http://adobe.com/AS3/2006/builtin', methodName='charAt', arguments=[1, 2.0], foundClass=None, foundFunction=None, foundResultHint=[], result=None, debug=False)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> bag
  bagForFindingInternalMethod(instance='abcdef', namespaceName='http://adobe.com/AS3/2006/builtin', methodName='charAt', arguments=[1, 2.0], foundClass=None, foundFunction=None, foundResultHint=[], result=None, debug=True)
  >>> bag.foundResultHint.append('summat strange')
  >>> bag.foundClass = string_Methods
  >>> bag.foundFunction = string_method_char_at
  >>> bag.result = 'myResult'
  >>> str(bag)[0:120]
  "bagForFindingInternalMethod(instance='abcdef', namespaceName='http://adobe.com/AS3/2006/builtin', methodName='charAt', a"
  >>> str(bag)[100:220]
  "thodName='charAt', arguments=[1, 2.0], foundClass=<class '__main__.string_Methods'>, foundFunction=<function string_meth"
  >>> str(bag)[200:233]
  'function string_method_char_at at'
  >>> str(bag)[-69:] # -70
  ">, foundResultHint=['summat strange'], result='myResult', debug=True)"
  >>> str(bag) # doctest: +ELLIPSIS
  "bagForFindingInternalMethod(instance='abcdef', namespaceName='http://adobe.com/AS3/2006/builtin', methodName='charAt', arguments=[1, 2.0], foundClass=<class '__main__.string_Methods'>, foundFunction=<function string_method_char_at at 0x...>, foundResultHint=['summat strange'], result='myResult', debug=True)"
  """
  instance: object # object whose method will be called
  namespaceName: str # namespace name # string internal methods = 'http://adobe.com/AS3/2006/builtin'
  methodName: str # method name
  arguments: list # arguments for method call
  foundClass: object = None # helper class that's been found
  # couldn't find a way to add to dict! # foundMethod: object = None # helper class method that's been found; probably a classmethod
  foundFunction: object = None # helper function to be used as class method
  foundResultHint: list = field(default_factory=list) # some feedback from the search process
  result: object = None # result after calling
  debug: bool = False # maybe add diagnostics

class findInternalMethod:
  @staticmethod
  def findClassAndMethodFromBag(bag: bagForFindingInternalMethod):
    """
    >>> # fails to find
    >>> myObj = 123.456
    >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
    >>> myMethod = 'charAt'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs)
    >>> findInternalMethod.findClassAndMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    'None'
    >>> str(bag.foundFunction)[:33]
    'None'
    >>> str(bag) # doctest: +ELLIPSIS
    'bagForFindingInternalMethod(instance=123.456, namespaceName=\\'http://adobe.com/AS3/2006/builtin\\', methodName=\\'charAt\\', arguments=[3], foundClass=None, foundFunction=None, foundResultHint=["@ai.p:fCAMFB:... in findClassAndMethodFromBag; no class <class \\'float\\'> + method <charAt> found"], result=None, debug=False)'
    >>> # should find
    >>> myObj = 'abcdef'
    >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
    >>> myMethod = 'charAt'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs)
    >>> findInternalMethod.findClassAndMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    "<class '__main__.string_Methods'>"
    >>> str(bag.foundFunction)[:34]
    '<function string_method_char_at at'
    >>> str(bag) # doctest: +ELLIPSIS
    "bagForFindingInternalMethod(instance='abcdef', namespaceName='http://adobe.com/AS3/2006/builtin', methodName='charAt', arguments=[3], foundClass=<class '__main__.string_Methods'>, foundFunction=<function string_method_char_at at 0x...>, foundResultHint=[], result=None, debug=False)"
    """
    for cls in [ string_Methods, Math_Object ]:
      cls.findMethodFromBag(bag)
      if bag.foundFunction: return
    bag.foundResultHint.append(f'@{BM.LINE(False)} in {inspect.stack()[0].function}; no class {type(bag.instance)} + method <{bag.methodName}> found')
  @staticmethod
  def perform(bag: bagForFindingInternalMethod):
    """
    >>> myObj = 'abcdef'
    >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
    >>> myMethod = 'charAt'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs)
    >>> findInternalMethod.findClassAndMethodFromBag(bag)
    >>> str(bag.foundClass)
    "<class '__main__.string_Methods'>"
    >>> str(bag.foundFunction)[:34]
    '<function string_method_char_at at'
    >>> findInternalMethod.perform(bag)
    >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    "<class '__main__.string_Methods'>"
    >>> str(bag.foundFunction)[:34]
    '<function string_method_char_at at'
    >>> str(bag.result)
    'd'
    >>> str(bag) # doctest: +ELLIPSIS
    "bagForFindingInternalMethod(instance='abcdef', namespaceName='http://adobe.com/AS3/2006/builtin', methodName='charAt', arguments=[3], foundClass=<class '__main__.string_Methods'>, foundFunction=<function string_method_char_at at 0x...>, foundResultHint=[], result='d', debug=False)"
    """
    if bag.foundFunction == None:
      bag.foundResultHint.append(f'@{BM.LINE(False)} in {inspect.stack()[0].function}; empty foundFunction')
      return
    bag.result = bag.foundFunction(bag.instance, *bag.arguments)

def Math_method_max(itemIgnored, *args):
  """
  Returns the maximum of two or more numbers
  >>> myObj = None
  >>> myItem1 = 123.45
  >>> myItem2 = 23
  >>> myNamespace ='Math'
  >>> myMethod = 'max'
  >>> myArgs = list()
  >>> myArgs.append(myItem1)
  >>> myArgs.append(myItem2)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = Math_method_max(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} MMMx_A {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  123.45
  >>> myItem1 = -123.45
  >>> myItem2 = 23
  >>> myNamespace ='Math'
  >>> myMethod = 'max'
  >>> myArgs = list()
  >>> myArgs.append(myItem1)
  >>> myArgs.append(myItem2)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = Math_method_max(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} MMMx_B {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  23
  >>> myItem1 = -123.45
  >>> myItem2 = 23
  >>> myItem3 = 234
  >>> myNamespace ='Math'
  >>> myMethod = 'max'
  >>> myArgs = list()
  >>> myArgs.append(myItem1)
  >>> myArgs.append(myItem2)
  >>> myArgs.append(myItem3)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = Math_method_max(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} MMMx_C {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  234
  """
  #print(f'@{BM.LINE()} MMMx called [{len(args)}] ({args})', file=sys.stderr)
  if len(args) < 2:
    raise NotImplementedError(f'@{BM.LINE()} expected 2+ args but {len(args)}')
  res = max(args)
  return res
def Math_method_min(itemIgnored, *args):
  """
  Returns the minimum of two or more numbers
  >>> myObj = None
  >>> myItem1 = 23.45
  >>> myItem2 = 123
  >>> myNamespace ='Math'
  >>> myMethod = 'min'
  >>> myArgs = list()
  >>> myArgs.append(myItem1)
  >>> myArgs.append(myItem2)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = Math_method_min(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} MMMn_A {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  23.45
  >>> myItem1 = 123.45
  >>> myItem2 = -23
  >>> myNamespace ='Math'
  >>> myMethod = 'min'
  >>> myArgs = list()
  >>> myArgs.append(myItem1)
  >>> myArgs.append(myItem2)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = Math_method_min(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} MMMn_B {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  -23
  >>> myItem1 = -23.45
  >>> myItem2 = 23
  >>> myItem3 = -234
  >>> myNamespace ='Math'
  >>> myMethod = 'min'
  >>> myArgs = list()
  >>> myArgs.append(myItem1)
  >>> myArgs.append(myItem2)
  >>> myArgs.append(myItem3)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = Math_method_min(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} MMMn_C {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  -234
  """
  #print(f'@{BM.LINE()} MMMn called [{len(args)}] ({args})', file=sys.stderr)
  if len(args) < 2:
    raise NotImplementedError(f'@{BM.LINE()} expected 2+ args but {len(args)}')
  res = min(args)
  return res
class Math_Object(RT.ASObject): # check https://help.adobe.com/en_US/FlashPlatform/reference/actionscript/3/Math.html

  dictSwfNameToMethod: ClassVar[dict[str, object]] = dict( \
    [ ('max', Math_method_max ) \
    , ('min', Math_method_min) \
    ])

  @classmethod
  def findMethodFromBag(cls, bag: bagForFindingInternalMethod):
    """
    >>> # no find
    >>> myObj = None
    >>> myNamespace ='MathUnknown'
    >>> myMethod = 'max'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> myArgs.append(4)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
    >>> Math_Object.findMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} FMFB_A {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    'None'
    >>> str(bag.foundFunction)[:33]
    'None'
    >>> # should not find
    >>> myObj = Math_Object_Singleton
    >>> myNamespace = '' # 'Math'
    >>> myMethod = 'maxUnknown'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
    >>> Math_Object.findMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} FMFB_B {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    'None'
    >>> str(bag.foundFunction)[:33]
    'None'
    >>> # should find
    >>> myObj = Math_Object_Singleton
    >>> myNamespace = '' # 'Math'
    >>> myMethod = 'max'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
    >>> Math_Object.findMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} FMFB_C {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    "<class '__main__.Math_Object'>"
    >>> str(bag.foundFunction)  # doctest: +ELLIPSIS
    '<function Math_method_max at 0x...'
    >>> # should find
    >>> myObj = Math_Object_Singleton
    >>> myNamespace = '' # 'Math'
    >>> myMethod = 'min'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
    >>> Math_Object.findMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} FMFB_D {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    "<class '__main__.Math_Object'>"
    >>> str(bag.foundFunction)  # doctest: +ELLIPSIS
    '<function Math_method_min at 0x...'
    """
    expectedNS = '' # was 'Math' but refactored out
    expectedInstanceClass = Math_Object

    if bag.namespaceName == expectedNS:
      #if True or isinstance(bag.instance, str): # TODO Check what object type is
      if isinstance(bag.instance, expectedInstanceClass): # TODO Check what object type is
        for k, v in cls.dictSwfNameToMethod.items():
          if k == bag.methodName:
            bag.foundClass = Math_Object
            bag.foundFunction = v
            if bag.debug: bag.foundResultHint.append(f'@{BM.LINE(False)} {cls.__name__} {type(bag.instance)} matched <{bag.methodName}> with {v}')
            return
        if bag.debug: bag.foundResultHint.append(f'@{BM.LINE(False)} {cls.__name__} {type(bag.instance)} could be Math but no match for <{bag.methodName}>')
      else:
        if bag.debug: bag.foundResultHint.append(f'@{BM.LINE(False)} {cls.__name__} {type(bag.instance)} not instance of {expectedInstanceClass}')
        pass
    else:
      if bag.debug: bag.foundResultHint.append(f'@{BM.LINE(False)} {cls.__name__} <{bag.namespaceName}> not expected namespace of <{expectedNS}>')
      pass
    return
Math_Object_Singleton = Math_Object(BM.LINE(False))

def string_method_char_at(item: str, index: int = 0):
  """
  Returns the character in the position specified by the index parameter.
  >>> myObj = 'abcdef'
  >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
  >>> myMethod = 'charAt'
  >>> myArgs = list()
  >>> myArgs.append(3)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = string_method_char_at(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} SMCA_A {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  'd'
  """
  res = item[index] # f'!! ## TODO: {inspect.stack()[0].function} ## !!'
  return res
def string_method_index_of(item: str, val: str, startIndex: int = 0) -> int:
  """
  Returns the character in the position specified by the index parameter.
  >>> myObj = 'abcdefa'
  >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
  >>> myMethod = 'indexOf'
  >>> myArgs = list()
  >>> myArgs.append('z')
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = string_method_index_of(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  -1
  >>> myArgs = list()
  >>> myArgs.append('a')
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = string_method_index_of(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  0
  >>> myArgs = list()
  >>> myArgs.append('a')
  >>> myArgs.append(1)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = string_method_index_of(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  6
  """
  res = item.find(val, startIndex)
  return res
def string_method_last_index_of(item: str, val: str, startIndex: int = 0x7fffffff) -> int:
  """
  Returns the character in the position specified by the index parameter.
  >>> myObj = 'abcdefa'
  >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
  >>> myMethod = 'lastIndexOf'
  >>> myArgs = list()
  >>> myArgs.append('z')
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = string_method_last_index_of(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  -1
  >>> myArgs = list()
  >>> myArgs.append('a')
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = string_method_last_index_of(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  6
  >>> myArgs = list()
  >>> myArgs.append('a')
  >>> myArgs.append(1)
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, debug=True)
  >>> res = string_method_last_index_of(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  0
  """
  res = item.rfind(val, 0, startIndex)
  return res
def string_method_substr(item: str, startIndex: int = 0, len: int = 0x7fffffff):
  """
  Returns a substring consisting of the characters that start at the specified startIndex and with a length specified by len.
  >>> myObj = 'abcdef'
  >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
  >>> myMethod = 'substr'
  >>> myArgs = list()
  >>> myArgs.append(1)
  >>> myArgs.append(4)
  >>> myObj[3:3]
  ''
  >>> myObj[3:4]
  'd'
  >>> myObj[1:4]
  'bcd'
  >>> myObj[myArgs[0]: myArgs[0]+myArgs[1]]
  'bcde'
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, '?c', '?m')
  >>> res = string_method_substr(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  'bcde'
  """
  res = item[startIndex:startIndex+len] # f'!! ## TODO: {inspect.stack()[0].function} ## !!'
  return res
def string_method_substring(item: str, startIndex: int = 0, endIndex: int = 0x7fffffff):
  """
  Returns a string consisting of the character specified by startIndex and all characters up to endIndex - 1
  >>> myObj = 'abcdef'
  >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
  >>> myMethod = 'substring'
  >>> #
  >>> # 2024-01-00
  >>> myArgs = list()
  >>> myArgs.append(1)
  >>> myArgs.append(4)
  >>> myObj[3:3]
  ''
  >>> myObj[3:4]
  'd'
  >>> myObj[1:4]
  'bcd'
  >>> myObj[myArgs[0]: myArgs[1] ]
  'bcd'
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, '?c', '?m')
  >>> res = string_method_substring(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  'bcd'
  >>> #
  >>> # 2024-01-21
  >>> myArgs = list()
  >>> myArgs.append(0)
  >>> myArgs.append(-1)
  >>> myObj[myArgs[0]: myArgs[1] ] # this is NOT what should happen
  'abcde'
  >>> myObj[myArgs[0]: 0 ] # this is what should happen
  ''
  >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs, '?c', '?m')
  >>> res = string_method_substring(bag.instance, *bag.arguments)
  >>> print(f'@{BM.LINE()} {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
  >>> res
  ''
  """
  if endIndex < 0: endIndex = 0 # this is what SHOULD happen
  res = item[startIndex:endIndex] # f'!! ## TODO: {inspect.stack()[0].function} ## !!'
  return res
class string_Methods: # check https://help.adobe.com/en_US/FlashPlatform/reference/actionscript/3/String.html

  dictSwfNameToMethod: ClassVar[dict[str, object]] = dict( \
    [ ('charAt', string_method_char_at ) \
    , ('indexOf', string_method_index_of) \
    , ('lastIndexOf', string_method_last_index_of) \
    , ('substr', string_method_substr) \
    , ('substring', string_method_substring) \
    ])

  @classmethod
  def findMethodFromBag(cls, bag: bagForFindingInternalMethod):
    """
    >>> # no find
    >>> myObj = 123.45
    >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
    >>> myMethod = 'charAt'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs)
    >>> string_Methods.findMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} FMFB_A {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> bag.foundClass
    >>> str(bag.foundClass)
    'None'
    >>> str(bag.foundFunction)[:33]
    'None'
    >>> # should not find
    >>> myObj = 'abcdef'
    >>> myNamespace = ''
    >>> myMethod = 'charAt'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs)
    >>> string_Methods.findMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} FMFB_B {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    'None'
    >>> str(bag.foundFunction)[:33]
    'None'
    >>> # should find
    >>> myObj = 'abcdef'
    >>> myNamespace ='http://adobe.com/AS3/2006/builtin'
    >>> myMethod = 'charAt'
    >>> myArgs = list()
    >>> myArgs.append(3)
    >>> bag = bagForFindingInternalMethod(myObj, myNamespace, myMethod, myArgs)
    >>> string_Methods.findMethodFromBag(bag)
    >>> print(f'@{BM.LINE()} FMFB_C {bag.foundResultHint}', file=sys.stderr) # check output for any hints of what went wrong
    >>> str(bag.foundClass)
    "<class '__main__.string_Methods'>"
    >>> str(bag.foundFunction)[:34]
    '<function string_method_char_at at'
    """
    expectedNS = 'http://adobe.com/AS3/2006/builtin'
    expectedInstanceClass = str

    if bag.namespaceName == expectedNS:
      if isinstance(bag.instance, expectedInstanceClass):
        for k, v in cls.dictSwfNameToMethod.items():
          if k == bag.methodName:
            bag.foundClass = string_Methods
            bag.foundFunction = v
            if bag.debug: bag.foundResultHint.append(f'@{BM.LINE(False)} {cls.__name__} {type(bag.instance)} matched <{bag.methodName}> with {v}')
            return
        if bag.debug: bag.foundResultHint.append(f'@{BM.LINE(False)} {cls.__name__} {type(bag.instance)} is a string but no match for <{bag.methodName}>')
      else:
        if bag.debug: bag.foundResultHint.append(f'@{BM.LINE(False)} {cls.__name__} {type(bag.instance)} not instance of {expectedInstanceClass}')
        pass
    else:
      if bag.debug: bag.foundResultHint.append(f'@{BM.LINE(False)} {cls.__name__} namespace <{bag.namespaceName}> not matching <{expectedNS}>')
      pass
    return


def read_instruction(reader: MemoryViewReader) -> Instruction: # only used by test_XXX_abc.py
    posAtStart = reader.position # mark start
    opcode: int = reader.read_u8()
    # noinspection PyCallingNonCallable
    inst = opcode_to_instruction[opcode](opcode, reader)
    posAtEnd = reader.position # mark end
    inst.instCodeLen = posAtEnd - posAtStart # calculate and save instruction code length
    return inst


u8 = NewType('u8', int)
u30 = NewType('u30', int)
uint = NewType('uint', int)
s24 = NewType('s24', int)

@dataclass
class Instruction:
    maxlastNInstr = 5 # maximum number of previous instructions to track
    readers: ClassVar[Dict[str, Callable[[MemoryViewReader], Any]]] = {
        u8.__name__: MemoryViewReader.read_u8,
        u30.__name__: MemoryViewReader.read_int,
        uint.__name__: MemoryViewReader.read_u32,
        s24.__name__: MemoryViewReader.read_s24,
    }

    # add some way to track things
    def tallyProgress(theInstance: Instruction, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment, offsetOfInstruction: int):
        environment.instrExeCnt += 1
        environment.lastNInstr.append(f'+{hex(offsetOfInstruction)} SS#{len(environment.scope_stack)}, OS#{len(environment.operand_stack)}, I={type(theInstance).__name__}')
        if len(environment.lastNInstr) > Instruction.maxlastNInstr:
          del environment.lastNInstr[0]

        # any callback?
        if environment.instrExeCnt == 1:
          print(f'\t{BM.LINE()}: {BM.TERM_CYN()}machine.cbOnInsExe is ={None if machine.cbOnInsExe == None else machine.cbOnInsExe.GetName()}{BM.TERM_RESET()}')
        if machine.cbOnInsExe is not None:
          machine.cbOnInsExe.ObserveInstructionExecuting(theInstance, machine, environment, offsetOfInstruction)

    opcode: int
    instCodeLen: int

    def __init__(self, opcode: int, reader: MemoryViewReader):
        posCodeStart = reader.position - 1  # Oops; unable to get actual start so calculate one byte back
        self.opcode = opcode
        for field in fields(self):
            if field.name == 'opcode': continue
            if field.name == 'instCodeLen': continue
            setattr(self, field.name, self.readers[field.type](reader))
        self.instCodeLen = reader.position - posCodeStart


    def doExecute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment, offsetOfInstruction: int) -> Optional[int]:
        self.tallyProgress(machine, environment, offsetOfInstruction)
        return self.execute(machine, environment)

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment) -> Optional[int]:
        raise NotImplementedError(self)

def instruction(opcode: int) -> Callable[[], Type[T]]:
  def wrapper(class_: Type[T]) -> Type[T]:
    assert opcode not in opcode_to_instruction, opcode_to_instruction[opcode]
    opcode_to_instruction[opcode] = class_
    class_.at_inst = opcode # helpful for testing
    return dataclass(init=False)(class_)
  return wrapper

T = TypeVar('T', bound=Instruction)
opcode_to_instruction: Dict[int, Type[T]] = {}


class ICallbackOnInstructionExecuting:
  """
  Derive your callback listener from here
  """
  def GetName(self) -> str:
    return type(self).__name__
  def ObserveInstructionExecuting(self, theInstruction: Instruction, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment, offsetOfInstruction: int):
    raise NotImplementedError(F'Someone forgot to override {BM.FUNC_NAME()}, or derive their listener from here ({self})')
  def MakeExtraObservation(self, extraObservation):
    raise NotImplementedError(F'Someone forgot to override {BM.FUNC_NAME()} ({self})')

@dataclass
class CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(ICallbackOnInstructionExecuting):
  """
  set limitCalls to -1 for all, or 0+ to limit the number of calls processed.
  tc = 'tab char'
  """
  limitCalls: int
  tc: str
  loggingLevel: int

  def ObserveInstructionExecuting(self, theInstruction: Instruction, machine: VirtualMachine, environment: MethodEnvironment, offsetOfInstruction: int):
    self.callsSoFar += 1
    strFinal = ' $FINAL$' if self.callsSoFar == self.limitCalls else ''

    if self.callsSoFar == 1 and self.callsSoFar <= self.limitCalls: # display on first call
      DumpEnvironmentRegisters(machine, environment)

    if (self.limitCalls < 0) or (self.limitCalls >= 0 and self.callsSoFar <= self.limitCalls):
      print(f'{self.tc}{BM.LINE(False)}: {theInstruction}{self.tc}{self.tc}// +{hex(offsetOfInstruction)} #{self.callsSoFar} SS#{len(environment.scope_stack)} OS#{len(environment.operand_stack)}{strFinal}')

  def MakeExtraObservation(self, extraObservation):
    if (self.limitCalls < 0) or (self.limitCalls >= 0 and self.callsSoFar <= self.limitCalls):
      callerF = inspect.currentframe() #getframeinfo(stack()[1][0])
      callerLine = callerF.f_back.f_lineno
      print(f'{self.tc}{BM.LINE(False)}: {self.tc}Extra@{callerLine}:{extraObservation}.')

  def GetLoggingLevel(self) -> int:
    return self.loggingLevel

  def __init__(self, limitCalls: int, tabChar: string = '\t', /, loggingLevel: int = logging.INFO):
    self.limitCalls = limitCalls
    self.callsSoFar: int = 0
    self.tc = tabChar
    self.loggingLevel = loggingLevel

def DummyTest():
  '''
  >>> DummyTest() # works fine # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  <BLANKLINE>
  <BLANKLINE>
  ai.p:MEO:...:  Extra@...:-os.pop value_2=<'value2'>.
  ai.p:MEO:...: Extra@...:-os.pop value_1=<'value1'>.
  <BLANKLINE>
  ai.p:MEO:...:   Extra@...:+os.push   result=<False>.
  '''
  #print("")
  print("  ai.p:MEO:602: \t\t\t Extra@1654:-os.pop value_2=<'value2'>. ")
  print("  \tai.p:MEO:602:  Extra@1656:-os.pop value_1=<'value1'>. ", end='')
  print("  ai.p:MEO:602:  Extra@1666:+os.push result=<False>.")
  #print("")
# Instructions implementation.
# ----------------------------------------------------------------------------------------------------------------------

@instruction(160)
class Add(Instruction): # …, value1, value2 => …, value3
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    result = value_1 + value_2
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)

@instruction(197)
class AddInteger(Instruction): # …, value1, value2 => …, value3
  """
  Pop value1 and value2 off of the stack and convert them to int values using the ToInt32
  algorithm (ECMA-262 section 9.5). Add the two int values and push the result onto the
  stack.
  """

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    result = int(value_1) + int(value_2)
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(134)
class AsType(Instruction):
  index: u30


@instruction(135)
class AsTypeLate(Instruction):
  pass


@instruction(168)
class BitAnd(Instruction):
  pass


@instruction(151)
class BitNot(Instruction):
  pass


@instruction(169)
class BitOr(Instruction):
  pass


@instruction(170)
class BitXor(Instruction):
  pass


@instruction(65)
class Call(Instruction): # …, function, receiver, arg1, arg2, ..., argn => …, value
  arg_count: u30


@instruction(67)
class CallMethod(Instruction): # …, receiver, arg1, arg2, ..., argn => …, value
  index: u30
  arg_count: u30


@instruction(70)
class CallProperty(Instruction): # …, obj, [ns], [name], arg1,...,argn => …, value
  """
  arg_count is a u30 that is the number of arguments present on the stack.
    The number of arguments specified by arg_count are popped off the stack and saved.

  index is a u30 that must be an index into the multiname constant pool.
    If the multiname at that index is a runtime multiname the name and/or namespace will also appear on the stack
      so that the multiname can be constructed correctly at runtime.

  obj is the object to resolve and call the property on.
    The property specified by the multiname at index is resolved on the object obj.

  The [[Call]] property is invoked on the value of the resolved property with the arguments obj, arg1, ..., argn.

  The result of the call is pushed onto the stack.

  >>> # 2024-01-19
  >>> inst = CallProperty(CallProperty.at_inst, MemoryViewReader(bytes(99)))
  >>> inst.index=1391
  >>> inst.arg_count=1
  >>> inst
  CallProperty(opcode=70, instCodeLen=3, index=1391, arg_count=1)
  >>> myVM = avm2.vm.VirtualMachine.from_Evony() # doctest: +ELLIPSIS
  @...
  >>> callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, '')
  >>> if True or False: myVM.cbOnInsExe = callback # this activates instruction logging and extra observations
  >>> myVM # doctest: +ELLIPSIS
  VirtualMachine(traceHint='v.p:fE:...#...', class_ix=None, properties={('', 'TheMainVm'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})
  >>> # <avm2.vm.VirtualMachine object at 0x...>
  >>> BM.DumpVar(myVM.global_object) # doctest: +ELLIPSIS
  "ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})"
  >>> scopeStack = [myVM.global_object]
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None,
          properties={('', 'Object'):                ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  >>> env = avm2.vm.MethodEnvironment.for_testing(5, scopeStack)
  >>> BM.DumpVar(env.registers) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[5]=[ASUndefined(traceHint='v.p:ft:...#0 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#1 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#2 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#3 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#4 #...', class_ix=None, properties={})]"
  >>>
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append('some:kinda:string')
  >>> env.operand_stack.append(':')
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[2]=['some:kinda:string', ':']"
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ai.p:MEO:...: Extra@...:ostack=<[2]=['some:kinda:string', ':']> CP_1.
    ai.p:MEO:...: Extra@...:-os.pop arg[0]=':'.
    ai.p:MEO:...: Extra@...:ostack=<[1]=['some:kinda:string']> CP_2.
    ai.p:MEO:...: Extra@...:get nam/ns from stack=False/False.
    ai.p:MEO:...: Extra@...:tSS#1=[1]=[ASObject(traceHint='v.p:__i_:...#...', class_ix=None,
          properties={('', 'Object'):                     ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={}),
                      ('', 'Math'):                       Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'):      ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})].
    ai.p:MEO:...: Extra@...:tN='indexOf'.
    ai.p:MEO:...: Extra@...:tNs='http://adobe.com/AS3/2006/builtin'.
    ai.p:MEO:...: Extra@...:-os.pop obj='some:kinda:string'.
    ai.p:MEO:...: Extra@...:ostack=<[0]=[]> CP_3.
    ai.p:MEO:...: Extra@...:+os.push result=<4>.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[1]=[4]'
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None,
          properties={('', 'Object'):                ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  >>>
  >>> # 2024-01-19
  >>> inst.index=1335
  >>> inst.arg_count=2
  >>> inst
  CallProperty(opcode=70, instCodeLen=3, index=1335, arg_count=2)
  >>> env.operand_stack.clear()
  >>> mathObject = Math_Object_Singleton # myVM.global_object.properties['', 'Math'] # get Math object
  >>> mathObject # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={})
  >>> env.operand_stack.append(mathObject)
  >>> env.operand_stack.append(45)
  >>> env.operand_stack.append(123.45)
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[3]=[Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}), 45, 123.45]"
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ai.p:MEO:...: Extra@...:ostack=<[3]=[Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}), 45, 123.45]> CP_1.
    ai.p:MEO:...: Extra@...:-os.pop arg[1]=123.45.
    ai.p:MEO:...: Extra@...:-os.pop arg[0]=45.
    ai.p:MEO:...: Extra@...:ostack=<[1]=[Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={})]> CP_2.
    ai.p:MEO:...: Extra@...:get nam/ns from stack=False/False.
    ai.p:MEO:...: Extra@...:tSS#1=[1]=[ASObject(traceHint='v.p:__i_:...#...', class_ix=None,
          properties={('', 'Object'):                     ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={}),
                      ('', 'Math'):                       Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'):      ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})].
    ai.p:MEO:...: Extra@...:tN='max'.
    ai.p:MEO:...: Extra@...:tNs=''.
    ai.p:MEO:...: Extra@...:-os.pop obj=Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}).
    ai.p:MEO:...: Extra@...:ostack=<[0]=[]> CP_3.
    ai.p:MEO:...: Extra@...:+os.push result=<123.45>.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[1]=[123.45]'
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None,
          properties={('', 'Object'):                ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}),
                      ('', 'Math'):                  Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  """
  index: u30
  arg_count: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> CP_1') # DEBUG

    multiname = machine.multinames[self.index]
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    #if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')

    argN=[]
    for ix in range(self.arg_count)[::-1]:
      theArg = environment.operand_stack.pop()
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop arg[{ix}]={BM.DumpVar(theArg)}')
      argN.insert(0, theArg)

    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> CP_2') # DEBUG

    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'get nam/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')

    theSStack = environment.scope_stack
    theName  = environment.operand_stack.pop() if getNamFromStk else machine.strings[multiname.nam_ix]
    theNS    = environment.operand_stack.pop() if getNsFromStk else machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]

    if machine.cbOnInsExe is not None:
      machine.cbOnInsExe.MakeExtraObservation(f'tSS#{len(theSStack)}={BM.DumpVar(theSStack)}')
      machine.cbOnInsExe.MakeExtraObservation(f'tN={BM.DumpVar(theName)}')
      machine.cbOnInsExe.MakeExtraObservation(f'tNs={BM.DumpVar(theNS)}')

    theObj = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop obj={BM.DumpVar(theObj)}')

    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> CP_3') # DEBUG

    bag = bagForFindingInternalMethod(theObj, theNS, theName, argN)
    if True: bag.debug = True # track bag process
    findInternalMethod.findClassAndMethodFromBag(bag)
    if bag.foundFunction:
      findInternalMethod.perform(bag)
      result = bag.result
    else:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'Internal Method failure, bag={bag}')
      assert False, f'@{BM.LINE(False)} Internal Method failure, tNs={BM.DumpVar(theNS)}, tN={BM.DumpVar(theName)}, bag={bag}'

    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(76)
class CallPropLex(Instruction): # …, obj, [ns], [name], arg1,...,argn => …, value
  index: u30
  arg_count: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(79)
class CallPropVoid(Instruction): # …, obj, [ns], [name], arg1,...,argn => …
  index: u30
  arg_count: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(68)
class CallStatic(Instruction): # …, receiver, arg1, arg2, ..., argn => …, value
  index: u30
  arg_count: u30


@instruction(69)
class CallSuper(Instruction):
  index: u30
  arg_count: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(78)
class CallSuperVoid(Instruction):
  index: u30
  arg_count: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(120)
class CheckFilter(Instruction):
  pass


@instruction(128)
class Coerce(Instruction):
  index: u30


@instruction(130)
class CoerceAny(Instruction):
  pass


@instruction(133)
class CoerceString(Instruction): # coerce_s # …, value => …, stringvalue
  """
  Coerce a value to a string.

  value is popped off of the stack and coerced to a String. If value is null or undefined, then stringvalue is set to null .
  Otherwise stringvalue is set to the result of the ToString algorithm, as specified in ECMA-262 section 9.8. stringvalue is pushed onto the stack.

  This opcode is very similar to the convert_s opcode.
  The difference is that convert_s will convert a null or undefined value to the string "null" or "undefined"
  whereas coerce_s will convert those values to the null value.

  >>> # 2024-01-18
  >>> inst = CoerceString(CoerceString.at_inst, MemoryViewReader(bytes(99)))
  >>> inst
  CoerceString(opcode=133, instCodeLen=1)
  >>> myVM = avm2.vm.VirtualMachine.from_Evony() # doctest: +ELLIPSIS
  @...
  >>> callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, '')
  >>> if True or False: myVM.cbOnInsExe = callback # this activates instruction logging and extra observations
  >>> myVM # doctest: +ELLIPSIS
  VirtualMachine(traceHint='v.p:fE:...#...', class_ix=None, properties={('', 'TheMainVm'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})
  >>> BM.DumpVar(myVM.global_object) # doctest: +ELLIPSIS
  "ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})"
  >>> scopeStack = [myVM.global_object]
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  >>> env = avm2.vm.MethodEnvironment.for_testing(5, scopeStack)
  >>>
  >>> # 2024-01-18
  >>> env.operand_stack.append('value1')
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['value1']"
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop 'value1' > +os.push 'value1'.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['value1']"
  >>> #
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append(123.45)
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[1]=[123.45]'
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop 123.45 > +os.push '123.45'.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['123.45']"
  >>> #
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append(None) # to None
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[1]=[None]'
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop None > +os.push None.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[1]=[None]'
  >>> #
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append(RT.undefined) # to None
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=[ASUndefined(traceHint='r.p:<:...', class_ix=None, properties={})]"
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop ASUndefined(traceHint='r.p:<:...', class_ix=None, properties={}) > +os.push None.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[1]=[None]'
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    valueRaw = environment.operand_stack.pop()
    value = None if RT.ValueIsNullOrUndefined(valueRaw) else f'{valueRaw}'
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop {BM.DumpVar(valueRaw)} > +os.push {BM.DumpVar(value)}')
    environment.operand_stack.append(value)


@instruction(66)
class Construct(Instruction): # …, object, arg1, arg2, ..., argn => …, value
  """
  arg_count is a u30 that is the number of arguments present on the stack. object is the
  function that is being constructed. This will invoke the [[Construct]] property on object with
  the given arguments. The new instance generated by invoking [[Construct]] will be pushed
  onto the stack.
  """
  arg_count: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}. BTW i={self.index} OS={environment.operand_stack}')
    print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}.{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_code.co_firstlineno}. BTW i={self.index}', file=sys.stderr)
    # TODO add proper code
    argN=[]
    for ix in range(self.arg_count)[::-1]:
      theArg = environment.operand_stack.pop()
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop arg[{ix}]={BM.DumpVar(theArg)}')
      argN.insert(0, theArg)

    theObj = environment.operand_stack.pop()

    result = f'!! ## TODO ## @{BM.LINE(False)} !!'
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(74)
class ConstructProp(Instruction): # …, obj, [ns], [name], arg1,...,argn => …, value
  """
  arg_count is a u30 that is the number of arguments present on the stack. The number of
  arguments specified by arg_count are popped off the stack and saved.

  index is a u30 that must be an index into the multiname constant pool. If the multiname at
  that index is a runtime multiname the name and/or namespace will also appear on the stack
  so that the multiname can be constructed correctly at runtime.

  obj is the object to resolve the multiname in.

  The property specified by the multiname at index is resolved on the object obj. The
  [[Construct]] property is invoked on the value of the resolved property with the arguments
  obj, arg1, ..., argn. The new instance generated by invoking [[Construct]] will be pushed
  onto the stack.
  """
  index: u30
  arg_count: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> CP_1') # DEBUG

    multiname = machine.multinames[self.index]
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    #if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')

    argN=[]
    for ix in range(self.arg_count)[::-1]:
      theArg = environment.operand_stack.pop()
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop arg[{ix}]={BM.DumpVar(theArg)}')
      argN.insert(0, theArg)

    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> CP_2') # DEBUG

    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'get nam/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')

    theSStack = environment.scope_stack
    theName  = environment.operand_stack.pop() if getNamFromStk else machine.strings[multiname.nam_ix]
    theNS    = environment.operand_stack.pop() if getNsFromStk else machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]

    if machine.cbOnInsExe is not None:
      machine.cbOnInsExe.MakeExtraObservation(f'tSS#{len(theSStack)}={BM.DumpVar(theSStack)}')
      machine.cbOnInsExe.MakeExtraObservation(f'tN={BM.DumpVar(theName)}')
      machine.cbOnInsExe.MakeExtraObservation(f'tNs={BM.DumpVar(theNS)}')

    theObj = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop obj={BM.DumpVar(theObj)}')

    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> CP_3') # DEBUG

    bag = bagForFindingInternalMethod(theObj, theNS, theName, argN)
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'bag=<{BM.DumpVar(bag)}> CP_4') # DEBUG
    findInternalMethod.findClassAndMethodFromBag(bag)
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'bag=<{BM.DumpVar(bag)}> CP_5') # DEBUG
    assert False, f'!! ## TODO ## @{BM.LINE(False)} Check Method as a [[Construct]] ... somehow !!'

    if bag.foundFunction:
      findInternalMethod.perform(bag)
      result = bag.result
    else:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'Internal Method failure, bag={bag}')
      assert False, f'@{BM.LINE(False)} Internal Method failure, bag={bag}'

    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(73)
class ConstructSuper(Instruction): # …, object, arg1, arg2, ..., argn => …
  """
  arg_count is a u30 that is the number of arguments present on the stack. This will invoke the
  constructor on the base class of object with the given arguments.
  """
  arg_count: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}. BTW i={self.index} OS={environment.operand_stack}')
    print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}.{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_code.co_firstlineno}. BTW i={self.index}', file=sys.stderr)
    # TODO add proper code
    #print(f'a#={self.arg_count}')
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'stack=<{BM.DumpVar(environment.operand_stack)}>')
    argN=[]
    for ix in range(self.arg_count)[::-1]:
      theArg = environment.operand_stack.pop()
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop arg[{ix}]={BM.DumpVar(theArg)}')
      print(f'arg[{ix}]={theArg}')
      argN.insert(0, theArg)

    theObj = environment.operand_stack.pop()

    # TODO Do something with theObj


@instruction(118)
class ConvertToBoolean(Instruction): # convert_b # …, value => …, booleanvalue
  """
  Convert a value to a Boolean.
  value is popped off of the stack and converted to a Boolean. The result, booleanvalue, is pushed onto the stack.
  This uses the ToBoolean algorithm, as described in ECMA-262 section 9.2, to perform the conversion.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    valueRaw = environment.operand_stack.pop()
    value = bool(valueRaw)
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop {BM.DumpVar(valueRaw)} > +os.push {BM.DumpVar(value)}')
    environment.operand_stack.append(value)


@instruction(115)
class ConvertToInteger(Instruction): # …, value => …, intvalue
  """
  `value` is popped off of the stack and converted to an integer. The result, `intvalue`, is pushed onto the stack.
  This uses the `ToInt32` algorithm, as described in ECMA-262 section 9.5, to perform the conversion.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    valueRaw = environment.operand_stack.pop()
    value = int(valueRaw)
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop {BM.DumpVar(valueRaw)} > +os.push {BM.DumpVar(value)}')
    environment.operand_stack.append(value)


@instruction(117)
class ConvertToDouble(Instruction): # …, value => …, doublevalue
  """
  `value` is popped off of the stack and converted to a double. The result, `doublevalue`, is pushed
  onto the stack. This uses the `ToNumber` algorithm, as described in ECMA-262 section 9.3,
  to perform the conversion.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    valueRaw = environment.operand_stack.pop()
    value = float(valueRaw)
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop {BM.DumpVar(valueRaw)} > +os.push {BM.DumpVar(value)}')
    environment.operand_stack.append(value)


@instruction(119)
class ConvertToObject(Instruction):
  pass


@instruction(116)
class ConvertToUnsignedInteger(Instruction):
  pass


@instruction(112)
class ConvertToString(Instruction): # convert_s # …, value => …, stringvalue
  """
  Convert a value to a string.

  value is popped off of the stack and converted to a string. The result, stringvalue, is pushed onto the stack.
  This uses the ToString algorithm, as described in ECMA-262 section 9.8

  This is very similar to the coerce_s opcode.
  The difference is that coerce_s will not convert a null or undefined value to the string "null" or "undefined" whereas convert_s will.

  >>> # 2024-01-18
  >>> inst = ConvertToString(ConvertToString.at_inst, MemoryViewReader(bytes(99)))
  >>> inst
  ConvertToString(opcode=112, instCodeLen=1)
  >>> myVM = avm2.vm.VirtualMachine.from_Evony() # doctest: +ELLIPSIS
  @...
  >>> callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, '')
  >>> if True or False: myVM.cbOnInsExe = callback # this activates instruction logging and extra observations
  >>> myVM # doctest: +ELLIPSIS
  VirtualMachine(traceHint='v.p:fE:...#...', class_ix=None, properties={('', 'TheMainVm'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})
  >>> BM.DumpVar(myVM.global_object) # doctest: +ELLIPSIS
  "ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})"
  >>> scopeStack = [myVM.global_object]
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  >>> env = avm2.vm.MethodEnvironment.for_testing(5, scopeStack)
  >>>
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append('value1')
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['value1']"
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop 'value1' > +os.push 'value1'.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['value1']"
  >>> #
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append(123.45)
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[1]=[123.45]'
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop 123.45 > +os.push '123.45'.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['123.45']"
  >>> #
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append(None) # to string 'Null'
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[1]=[None]'
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop None > +os.push 'null'.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['null']"
  >>> #
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append(RT.undefined) # to string 'Undefined')
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=[ASUndefined(traceHint='r.p:<:...', class_ix=None, properties={})]"
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop ASUndefined(traceHint='r.p:<:...', class_ix=None, properties={}) > +os.push 'undefined'.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['undefined']"
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    valueRaw = environment.operand_stack.pop()
    if False: pass
    elif RT.ValueIsNull(valueRaw):
      value = 'null'
    elif RT.ValueIsNullOrUndefined(valueRaw):
      value = 'undefined'
    else:
      value = f'{valueRaw}'
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop {BM.DumpVar(valueRaw)} > +os.push {BM.DumpVar(value)}')
    environment.operand_stack.append(value)


@instruction(239)
class Debug(Instruction):
  debug_type: u8
  index: u30
  reg: u8
  extra: u30


@instruction(241)
class DebugFile(Instruction):
  index: u30


@instruction(240)
class DebugLine(Instruction):
  linenum: u30


@instruction(148)
class DecLocal(Instruction):
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    lenEnvReg = len(environment.registers)
    assert self.index < lenEnvReg, f'index {self.index} not < lenEnvReg {lenEnvReg}'
    value = environment.registers[self.index]
    result = value - 1
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
    environment.registers[self.index] = result


@instruction(195)
class DecLocalInteger(Instruction):
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    lenEnvReg = len(environment.registers)
    assert self.index < lenEnvReg, f'index {self.index} not < lenEnvReg {lenEnvReg}'
    value = environment.registers[self.index]
    result = int(value) - 1
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
    environment.registers[self.index] = result


@instruction(147)
class Decrement(Instruction): # …, value => …, decrementedvalue
  """
  Pop value off of the stack.
  Convert value to a Number using the ToNumber algorithm (ECMA-262 section 9.3) and then subtract 1 from the Number value.
  Push the result onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    result = value - 1
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop, +os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(193)
class DecrementInteger(Instruction): # …, value => …, decrementedvalue
  """
  Pop value off of the stack.
  Convert value to an int using the ToInt32 algorithm (ECMA-262 section 9.5) and then subtract 1 from the int value.
  Push the result onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    result = int(value) - 1
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop, +os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(106)
class DeleteProperty(Instruction):
  index: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(163)
class Divide(Instruction): # …, value1, value2 => …, value3
  """
  Pop `value1` and `value2` off of the stack, convert `value1` and `value2` to `Number` to create
  `value1_number` and `value2_number`. Divide `value1_number` by `value2_number` and push the
  result onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    result = value_1 / value_2
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(42)
class Dup(Instruction): # …, value => …, value, value
  """
  Duplicates the top value of the stack, and then pushes the duplicated value onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.extend([value, value])


@instruction(6)
class DXNS(Instruction):
  index: u30


@instruction(7)
class DXNSLate(Instruction):
  pass


@instruction(171)
class EqualsOperation(Instruction): # equals # …, value1, value2 => …, result
  """
  Compare two values.
  Pop value1 and value2 off of the stack.
  Compare the two values using the abstract equality comparison algorithm, as described in ECMA-262 section 11.9.3 and extended in ECMA-347 section 11.5.1.
  Push the resulting Boolean value onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    result = value_1 == value_2
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(114)
class EscXAttr(Instruction):
  pass


@instruction(113)
class EscXElem(Instruction):
  pass


@instruction(94)
class FindProperty(Instruction): # …, [ns], [name] => …, obj
  """
  index is a u30 that must be an index into the multiname constant pool. If the multiname at
  that index is a runtime multiname the name and/or namespace will also appear on the stack
  so that the multiname can be constructed correctly at runtime.

  This searches the scope stack, and then the saved scope in the current method closure, for a
  property with the name specified by the multiname at index.

  If any of the objects searched is a with scope, its declared and dynamic properties will be
  searched for a match. Otherwise only the declared traits of a scope will be searched. The
  global object will have its declared traits, dynamic properties, and prototype chain searched.

  If the property is resolved then the object it was resolved in is pushed onto the stack. If the
  property is unresolved in all objects on the scope stack then the global object is pushed onto
  the stack.
  """
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> CP_1') # DEBUG

    multiname = machine.multinames[self.index]
    # TODO: other kinds of multinames.
    assert multiname.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A), multiname

    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'get nam/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')

    try:
      theSStack     = environment.scope_stack
      theName       = environment.operand_stack.pop() if getNamFromStk else machine.strings[multiname.nam_ix]
      theNamespaces = [environment.operand_stack.pop()] if getNsFromStk else [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]]

      if machine.cbOnInsExe is not None:
        #machine.cbOnInsExe.MakeExtraObservation(f'tSS#{len(theSStack)}={BM.DumpVar(theSStack)}')
        machine.cbOnInsExe.MakeExtraObservation(f'tN={BM.DumpVar(theName)}')
        machine.cbOnInsExe.MakeExtraObservation(f'tNs={BM.DumpVar(theNamespaces)}')
      object_, name, namespace, scopeStackEntry = machine.resolve_multiname(
          theSStack, # environment.scope_stack,
          theName, # stack or machine.strings[multiname.nam_ix],
          theNamespaces # [stack or machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]],
      )
    except KeyError as excp:
      raise NotImplementedError(f'ReferenceError < KeyError({excp})')
    else:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push object_=<{BM.DumpVar(object_)}> type={type(object_)}')
      environment.operand_stack.append(object_)
      assert len(environment.operand_stack) < 55, 'Crash Here'

@instruction(93)
class FindPropStrict(Instruction): # …, [ns], [name] => …, obj
  """
  `index` is a `u30` that must be an index into the `multiname` constant pool. If the multiname at
  that index is a runtime multiname the name and/or namespace will also appear on the stack
  so that the multiname can be constructed correctly at runtime.

  This searches the scope stack, and then the saved scope in the method closure, for a property
  with the name specified by the multiname at `index`.

  If any of the objects searched is a `with` scope, its declared and dynamic properties will be
  searched for a match. Otherwise only the declared traits of a scope will be searched. The
  global object will have its declared traits, dynamic properties, and prototype chain searched.

  If the property is resolved then the object it was resolved in is pushed onto the stack. If the
  property is unresolved in all objects on the scope stack then an exception is thrown.

  A `ReferenceError` is thrown if the property is not resolved in any object on the scope stack.
  """
  index: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> CP_1') # DEBUG

    multiname = machine.multinames[self.index]
    # TODO: other kinds of multinames.
    assert multiname.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A), multiname

    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'get nam/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')

    try:
      theSStack     = environment.scope_stack
      theName       = environment.operand_stack.pop() if getNamFromStk else machine.strings[multiname.nam_ix]
      theNamespaces = [environment.operand_stack.pop()] if getNsFromStk else [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]]

      if machine.cbOnInsExe is not None:
        #machine.cbOnInsExe.MakeExtraObservation(f'tSS#{len(theSStack)}={BM.DumpVar(theSStack)}')
        machine.cbOnInsExe.MakeExtraObservation(f'tN={BM.DumpVar(theName)}')
        machine.cbOnInsExe.MakeExtraObservation(f'tNs={BM.DumpVar(theNamespaces)}')
      object_, name, namespace, scopeStackEntry = machine.resolve_multiname(
          theSStack, # environment.scope_stack,
          theName, # stack or machine.strings[multiname.nam_ix],
          theNamespaces # [stack or machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]],
      )
    except KeyError:
      raise NotImplementedError('ReferenceError')
    else:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push object_=<{BM.DumpVar(object_)}> type={type(object_)}')
      environment.operand_stack.append(object_)
      assert len(environment.operand_stack) < 55, 'Crash Here'

@instruction(89)
class GetDescendants(Instruction):
  index: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(100)
class GetGlobalScope(Instruction):
  pass


@instruction(110)
class GetGlobalSlot(Instruction):
  slot_ix: u30


@instruction(96)
class GetLex(Instruction): # … => …, obj
  """
  `index` is a `u30` that must be an index into the multiname constant pool. The multiname at
  `index` must not be a runtime multiname, so there are never any optional namespace or name
  values on the stack.

  This is the equivalent of doing a `findpropstrict` followed by a `getproperty`. It will find the
  object on the scope stack that contains the property, and then will get the value from that
  object. See "Resolving multinames" on page 10.

  A `ReferenceError` is thrown if the property is unresolved in all of the objects on the scope
  stack.

  >>> # 2024-01-19
  >>> inst = GetLex(GetLex.at_inst, MemoryViewReader(bytes(99)))
  >>> inst.index=1334
  >>> inst
  GetLex(opcode=96, instCodeLen=2, index=1334)
  >>> myVM = avm2.vm.VirtualMachine.from_Evony() # doctest: +ELLIPSIS
  @...
  >>> callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, '', loggingLevel = logging.DEBUG)
  >>> if True or False: myVM.cbOnInsExe = callback # this activates instruction logging and extra observations
  >>> myVM # doctest: +ELLIPSIS
  VirtualMachine(traceHint='v.p:fE:...#...', class_ix=None, properties={('', 'TheMainVm'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})
  >>> BM.DumpVar(myVM.global_object) # doctest: +ELLIPSIS
  "ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})"
  >>> scopeStack = [myVM.global_object]
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None,
          properties={('', 'Object'):                ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  >>> env = avm2.vm.MethodEnvironment.for_testing(5, scopeStack)
  >>> BM.DumpVar(env.registers) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[5]=[ASUndefined(traceHint='v.p:ft:...#0 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#1 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#2 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#3 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#4 #...', class_ix=None, properties={})]"
  >>>
  >>> # 2024-01-19
  >>> env.operand_stack.clear()
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[0]=[]'
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE, +REPORT_NDIFF
    ai.p:MEO:...: Extra@...:mn=ASMultinameBis(kind=<MultinameKind.Q_NAME: 7>, ns_ix=2, nam_ix=1332, ns_set_ix=None, q_nam_ix=None, type_ixs=None, ixCP=1334, ns_name='', nam_name='Math', ns_set_names=None, q_nam_name=None).
    ai.p:MEO:...: Extra@...:tSS#1=[1]=[ASObject(traceHint='v.p:__i_:...#...', class_ix=None,
          properties={('', 'Object'):                     ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={}),
                      ('', 'Math'):                       Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'):      ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})].
    ai.p:MEO:...: Extra@...: [0] props#3.
    ai.p:MEO:...: Extra@...:  props[ns='', n='Object'] = ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={}).
    ai.p:MEO:...: Extra@...:  props[ns='', n='Math'] = Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}).
    ai.p:MEO:...: Extra@...:  props[ns='flash.utils', n='Dictionary'] = ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={}).
    ai.p:MEO:...: Extra@...:tN='Math'.
    ai.p:MEO:...: Extra@...:tNs=[1]=[''].
    ai.p:MEO:...: Extra@...:(v.p)ResMulNam.name=<'Math'> SS#=1.
    ai.p:MEO:...: Extra@...:(v.p) ResMulNam.sobj=<ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={}), ('', 'Math'): Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})>.
    ai.p:MEO:...: Extra@...:(v.pD)  ResQNam try ns ''.
    ai.p:MEO:...: Extra@...:object_=Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={}), namespace='', name='Math'.
    ai.p:MEO:...: Extra@...:+os.push result=<Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={})>.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=[Math_Object(traceHint='ai.p:<:...#...', class_ix=None, properties={})]"
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None,
          properties={('', 'Object'):                ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  """
  index: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    multiname = machine.multinames[self.index]
    assert multiname.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A)
    hint = '?'
    hint = 'tS';   theSStack     = environment.scope_stack
    hint = 'tN';   theName       = machine.strings[multiname.nam_ix]
    hint = 'tNSs'; theNamespaces = [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]]
    hint = 'm.cOIE';
    if machine.cbOnInsExe is not None:
      machine.cbOnInsExe.MakeExtraObservation(f'mn={BM.DumpVar(multiname)}')
      machine.cbOnInsExe.MakeExtraObservation(f'tSS#{len(theSStack)}={BM.DumpVar(theSStack)}')
      if machine.cbOnInsExe.GetLoggingLevel() == logging.DEBUG:
        for ix in range(len(theSStack)):
          item = theSStack[ix]
          machine.cbOnInsExe.MakeExtraObservation(f' [{ix}] props#{len(item.properties)}')
          for keyNS_N in item.properties:
            itemL = item.properties[keyNS_N]
            if len(keyNS_N) == 2:
              machine.cbOnInsExe.MakeExtraObservation(f'  props[ns={BM.DumpVar(keyNS_N[0])}, n={BM.DumpVar(keyNS_N[1])}] = {BM.DumpVar(itemL)}')
            else:
              machine.cbOnInsExe.MakeExtraObservation(f'  props[{keyNS_N}] (k#{len(keyNS_N)}) = {BM.DumpVar(itemL)}')

      machine.cbOnInsExe.MakeExtraObservation(f'tN={BM.DumpVar(theName)}')
      machine.cbOnInsExe.MakeExtraObservation(f'tNs={BM.DumpVar(theNamespaces)}')
    try:
      hint = 'm.rmn';object_, name, namespace, scopeStackEntry = machine.resolve_multiname(
          theSStack, # environment.scope_stack,
          theName, # machine.strings[multiname.nam_ix],
          theNamespaces, # [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]],
      )
    except KeyError as err:
      print(f'@{BM.LINE()} HACK SHOULD STOP BUT I WANT TO SEE NEXT BIT err={err}: ReferenceError: hint={hint}') # HACK
      # HACK must uncomment this # raise NotImplementedError(f'err={err}: ReferenceError: hint={hint}') # HACK must uncomment this
    else:
      if machine.cbOnInsExe and machine.cbOnInsExe.GetLoggingLevel() == logging.DEBUG:
        machine.cbOnInsExe.MakeExtraObservation(f'object_={BM.DumpVar(object_)}, namespace={BM.DumpVar(namespace)}, name={BM.DumpVar(name)}')
      # NO! no need to access via key result = object_.properties[namespace, name]
      result = object_
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
      environment.operand_stack.append(result)


@instruction(98)
class GetLocal(Instruction): # … => …, value
  """
  Get a local register.
  index is a u30 that must be an index of a local register. The value of that register is pushed onto the stack.
  """
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    assert self.index < len(environment.registers)
    value = environment.registers[self.index]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    # if machine.cbOnInsExe is not None: DumpEnvironmentRegisters(machine, environment)
    environment.operand_stack.append(value)

def DumpEnvironmentRegisters(machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
  if machine.cbOnInsExe is not None:
    lenEnvReg = len(environment.registers)
    machine.cbOnInsExe.MakeExtraObservation(f'BTW #ER={BM.DumpVar(lenEnvReg)} SS#{len(environment.scope_stack)} OS#{len(environment.operand_stack)}')
    for ix in range(lenEnvReg):
      machine.cbOnInsExe.MakeExtraObservation(f'BTW ER{ix}={BM.DumpVar(environment.registers[ix])}')

@instruction(208)
class GetLocal0(Instruction): # … => …, value
  """
  `<n>` is the index of a local register. The value of that register is pushed onto the stack.

  >>> # 2024-01-19
  >>> inst = GetLocal0(GetLocal0.at_inst, MemoryViewReader(bytes(99)))
  >>> inst
  GetLocal0(opcode=208, instCodeLen=1)
  >>> myVM = avm2.vm.VirtualMachine.from_Evony() # doctest: +ELLIPSIS
  @...
  >>> callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, '')
  >>> if True or False: myVM.cbOnInsExe = callback # this activates instruction logging and extra observations
  >>> myVM # doctest: +ELLIPSIS
  VirtualMachine(traceHint='v.p:fE:...#...', class_ix=None, properties={('', 'TheMainVm'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})
  >>> BM.DumpVar(myVM.global_object) # doctest: +ELLIPSIS
  "ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})"
  >>> scopeStack = [myVM.global_object]
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  >>> env = avm2.vm.MethodEnvironment.for_testing(5, scopeStack)
  >>> BM.DumpVar(env.registers) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[5]=[ASUndefined(traceHint='v.p:ft:...#0 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#1 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#2 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#3 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#4 #...', class_ix=None, properties={})]"
  >>>
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[0]=[]'
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:+os.push value=<ASUndefined(traceHint='v.p:ft:...#0 #...', class_ix=None, properties={})>.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=[ASUndefined(traceHint='v.p:ft:...#0 #...', class_ix=None, properties={})]"
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.registers[0]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    # if machine.cbOnInsExe is not None: DumpEnvironmentRegisters(machine, environment)
    environment.operand_stack.append(value)


@instruction(209)
class GetLocal1(Instruction): # … => …, value
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.registers[1]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    # if machine.cbOnInsExe is not None: DumpEnvironmentRegisters(machine, environment)
    environment.operand_stack.append(value)


@instruction(210)
class GetLocal2(Instruction): # … => …, value
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.registers[2]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    # if machine.cbOnInsExe is not None: DumpEnvironmentRegisters(machine, environment)
    environment.operand_stack.append(value)


@instruction(211)
class GetLocal3(Instruction): # … => …, value
  """
  `<n>` is the index of a local register. The value of that register is pushed onto the stack.

  >>> # 2024-01-19
  >>> inst = GetLocal3(GetLocal3.at_inst, MemoryViewReader(bytes(99)))
  >>> inst
  GetLocal3(opcode=211, instCodeLen=1)
  >>> myVM = avm2.vm.VirtualMachine.from_Evony() # doctest: +ELLIPSIS
  @...
  >>> callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, '')
  >>> if True or False: myVM.cbOnInsExe = callback # this activates instruction logging and extra observations
  >>> myVM # doctest: +ELLIPSIS
  VirtualMachine(traceHint='v.p:fE:...#...', class_ix=None, properties={('', 'TheMainVm'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})
  >>> BM.DumpVar(myVM.global_object) # doctest: +ELLIPSIS
  "ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})"
  >>> scopeStack = [myVM.global_object]
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  >>> env = avm2.vm.MethodEnvironment.for_testing(5, scopeStack)
  >>> BM.DumpVar(env.registers) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[5]=[ASUndefined(traceHint='v.p:ft:...#0 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#1 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#2 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#3 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#4 #...', class_ix=None, properties={})]"
  >>>
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[0]=[]'
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:+os.push value=<ASUndefined(traceHint='v.p:ft:...#3 #...', class_ix=None, properties={})>.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=[ASUndefined(traceHint='v.p:ft:...#3 #...', class_ix=None, properties={})]"
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.registers[3]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    # if machine.cbOnInsExe is not None: DumpEnvironmentRegisters(machine, environment)
    environment.operand_stack.append(value)


@instruction(102)
class GetProperty(Instruction):
  index: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(101)
class GetScopeObject(Instruction): # … => …, scope
  """
  `index` is an unsigned byte that specifies the index of the scope object to retrieve from the local
  scope stack. `index` must be less than the current depth of the scope stack. The scope at that
  `index` is retrieved and pushed onto the stack. The scope at the top of the stack is at index
  `scope_depth - 1`, and the scope at the bottom of the stack is index `0`.
  """
  index: u8

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.scope_stack[self.index]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.append(value)


@instruction(108)
class GetSlot(Instruction):
  slot_ix: u30


@instruction(4)
class GetSuper(Instruction):
  index: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(176)
class GreaterEquals(Instruction): # …, value1, value2 => …, result
  """
  Pop `value1` and `value2` off of the stack. Compute `value1 < value2` using the Abstract
  Relational Comparison Algorithm, as described in ECMA-262 section 11.8.5. If the result of
  the comparison is `false`, push `true` onto the stack. Otherwise push `false` onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    result = value_1 >= value_2
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(175)
class GreaterThan(Instruction): # …, value1, value2 => …, result
  """
  Determine if one value is greater than another.
  Pop 'value1' and 'value2' off of the stack. Compute value2 < value1 using the Abstract Relational Comparison Algorithm as described in ECMA-262 section 11.8.5.
  If the result of the comparison is 'true', push 'true' onto the stack. Otherwise push 'false' onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    """
    >>> # 2024-01-17
    >>> # GreaterThan.__name__, GreaterThan.at_opcode # ('GreaterThan', 175)
    >>> inst = GreaterThan(GreaterThan.at_inst, MemoryViewReader(bytes(99)))
    >>> inst
    GreaterThan(opcode=175, instCodeLen=1)
    >>> myVM = avm2.vm.VirtualMachine.from_Evony() # doctest: +ELLIPSIS
    @...
    >>> callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, ' ')
    >>> if True or False: myVM.cbOnInsExe = callback # this activates instruction logging and extra observations
    >>> myVM # doctest: +ELLIPSIS
    VirtualMachine(traceHint='v.p:fE:...#...', class_ix=None, properties={('', 'TheMainVm'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})
    >>> BM.DumpVar(myVM.global_object) # doctest: +ELLIPSIS
    "ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})"
    >>> scopeStack = [myVM.global_object]
    >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS
    "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
    >>> env = avm2.vm.MethodEnvironment.for_testing(5, scopeStack)
    >>> #
    >>> # 2024-01-17
    >>> env.operand_stack.clear()
    >>> env.operand_stack.append('value1')
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    "[1]=['value1']"
    >>> env.operand_stack.append('value2')
    >>> print(' abc');
     abc
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    "[2]=['value1', 'value2']"
    >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ai.p:MEO:...:  Extra@...:-os.pop value_2=<'value2'>.
    ai.p:MEO:...:  Extra@...:-os.pop value_1=<'value1'>.
    ai.p:MEO:...:  Extra@...:+os.push result=<False>.
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    '[1]=[False]'
    >>> #
    >>> # 2024-01-17
    >>> env.operand_stack.clear()
    >>> env.operand_stack.append('value1')
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    "[1]=['value1']"
    >>> env.operand_stack.append('value02')
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    "[2]=['value1', 'value02']"
    >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ai.p:MEO:...:  Extra@...:-os.pop value_2=<'value02'>.
    ai.p:MEO:...:  Extra@...:-os.pop value_1=<'value1'>.
    ai.p:MEO:...:  Extra@...:+os.push result=<True>.
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    '[1]=[True]'
    >>> #
    >>> # 2024-01-17
    >>> env.operand_stack.clear()
    >>> env.operand_stack.append('value1')
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    "[1]=['value1']"
    >>> env.operand_stack.append('value1')
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    "[2]=['value1', 'value1']"
    >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ai.p:MEO:...:  Extra@...:-os.pop value_2=<'value1'>.
    ai.p:MEO:...:  Extra@...:-os.pop value_1=<'value1'>.
    ai.p:MEO:...:  Extra@...:+os.push result=<False>.
    >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
    '[1]=[False]'
    """
    #if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f' @@##$$ $$##@@ =<{BM.DumpVar(GetLocal0.at_opcode)}>') # DEBUG
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    result = value_1 > value_2
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)

@instruction(31)
class HasNext(Instruction):
  pass


@instruction(50)
class HasNext2(Instruction):
  object_reg: uint
  index_reg: uint


@instruction(19)
class IfEq(Instruction): # …, value1, value2 => …
  """
  Branch if the first value is equal to the second value.
  offset is an s24 that is the number of bytes to jump if value1 is equal to value2.
  Compute value1 == value2 using the abstract equality comparison algorithm in ECMA-262 section 11.9.3 and ECMA-347 section 11.5.1.
  If the result of the comparison is true , jump the number of bytes indicated by offset. Otherwise continue executing code from this point.
  """
  offset: s24
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    if value_1 == value_2:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'jump {self.offset} {strBACKWARDS_n if self.offset < 0 else ""}')
      raise ASJumpException(self.offset)


@instruction(18)
class IfFalse(Instruction): # …, value => …
  """
  Pop value off the stack and convert it to a `Boolean`. If the converted value is `false`, jump the
  number of bytes indicated by `offset`. Otherwise continue executing code from this point.
  """

  offset: s24

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    if not value:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'jump {self.offset} {strBACKWARDS_n if self.offset < 0 else ""}')
      raise ASJumpException(self.offset)


@instruction(24)
class IfGE(Instruction):
  offset: s24


@instruction(23)
class IfGT(Instruction):
  offset: s24


@instruction(22)
class IfLE(Instruction):
  offset: s24


@instruction(21)
class IfLT(Instruction): # …, value1, value2 => …
  """
  `offset` is an `s24` that is the number of bytes to jump if `value1` is less than `value2`.

  Compute value1 < value2 using the abstract relational comparison algorithm in ECMA-262
  section 11.8.5. If the result of the comparison is `true`, jump the number of bytes indicated
  by `offset`. Otherwise continue executing code from this point.
  """
  offset: s24

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    if value_1 < value_2:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'jump {self.offset} {strBACKWARDS_n if self.offset < 0 else ""}')
      raise ASJumpException(self.offset)


@instruction(15)
class IfNGE(Instruction):
  offset: s24


@instruction(14)
class IfNGT(Instruction): # …, value1, value2 => …
  """
  Compute `value2 < value1` using the abstract relational comparison algorithm in ECMA-262
  section 11.8.5. If the result of the comparison is not `true`, jump the number of bytes
  indicated by `offset`. Otherwise continue executing code from this point.
  """

  offset: s24

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    # FIXME: NaN.
    if not value_1 > value_2:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'jump {self.offset} {strBACKWARDS_n if self.offset < 0 else ""}')
      raise ASJumpException(self.offset)


@instruction(13)
class IfNLE(Instruction):
  offset: s24


@instruction(12)
class IfNLT(Instruction): # …, value1, value2 => …
  """
  Compute `value1 < value2` using the abstract relational comparison algorithm in ECMA-262
  section 11.8.5. If the result of the comparison is false, then jump the number of bytes
  indicated by `offset`. Otherwise continue executing code from this point.

  This appears to have the same effect as `ifge`, however, their handling of `NaN` is different. If
  either of the compared values is `NaN` then the comparison `value1 < value2` will return
  `undefined`. In that case `ifnlt` will branch (`undefined` is not true), but `ifge` will not
  branch.
  """

  offset: s24

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    # FIXME: NaN.
    if not value_1 < value_2:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'jump {self.offset} {strBACKWARDS_n if self.offset < 0 else ""}')
      raise ASJumpException(self.offset)


@instruction(20)
class IfNE(Instruction):
  """
  Compute `value1 == value2` using the abstract relational comparison algorithm in ECMA-262
  section 11.8.5. If the result of the comparison is false, then jump the number of bytes
  indicated by `offset`. Otherwise continue executing code from this point.
  """

  offset: s24

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    # FIXME: NaN. maybe
    if not value_1 == value_2:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'jump {self.offset} {strBACKWARDS_n if self.offset < 0 else ""}')
      raise ASJumpException(self.offset)


@instruction(25)
class IfStrictEq(Instruction):
  offset: s24


@instruction(26)
class IfStrictNE(Instruction):
  offset: s24


@instruction(17)
class IfTrue(Instruction):
  """
  Pop value off the stack and convert it to a `Boolean`. If the converted value is `true`, jump the
  number of bytes indicated by `offset`. Otherwise continue executing code from this point.
  """
  offset: s24

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    if value:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'jump {self.offset} {strBACKWARDS_n if self.offset < 0 else ""}')
      raise ASJumpException(self.offset)


@instruction(180)
class In(Instruction): # …, name, obj => …, result
  """
  Determine whether an object has a named property.
  name is converted to a String, and is looked up in obj.
  If no property is found, then the prototype chain is searched by calling [[HasProperty]] on the prototype of obj.
  If the property is found result is true . Otherwise result is false .
  Push result onto the stack.
  """
  pass


@instruction(146)
class IncLocal(Instruction): # … => …
  """
  index is a u30 that must be an index of a local register.
  The value of the local register at index is converted to a Number using the ToNumber algorithm (ECMA-262 section 9.3) and then 1 is added to the Number value.
  The local register at index is then set to the result.
  """
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    lenEnvReg = len(environment.registers)
    assert self.index < lenEnvReg, f'index {self.index} not < lenEnvReg {lenEnvReg}'
    value = environment.registers[self.index]
    result = value + 1
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
    environment.registers[self.index] = result

@instruction(194)
class IncLocalInteger(Instruction): # … => …
  """
  index is a u30 that must be an index of a local register.
  The value of the local register at index is converted to an int using the ToInt32 algorithm (ECMA-262 section 9.5) and then 1 is added to the int value.
  The local register at index is then set to the result.
  """
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    lenEnvReg = len(environment.registers)
    assert self.index < lenEnvReg, f'index {self.index} not < lenEnvReg {lenEnvReg}'
    value = environment.registers[self.index]
    result = int(value) + 1
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
    environment.registers[self.index] = result


@instruction(145)
class Increment(Instruction): # …, value => …, incrementedvalue
  """
  Pop value off of the stack.
  Convert value to a Number using the ToNumber algorithm (ECMA-262 section 9.3) and then add 1 to the Number value.
  Push the result onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    result = value + 1
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop, +os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(192)
class IncrementInteger(Instruction): # …, value => …, incrementedvalue
  """
  Pop value off of the stack.
  Convert value to an int using the ToInt32 algorithm (ECMA-262 section 9.5) and then add 1 to the int value.
  Push the result onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    result = int(value) + 1
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop, +os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(104)
class InitProperty(Instruction): # …, object, [ns], [name], value => …
  index: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'ostack=<{BM.DumpVar(environment.operand_stack)}> IP_1') # DEBUG

    multiname = machine.multinames[self.index]
    # TODO: other kinds of multinames.
    assert multiname.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A), multiname

    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')

    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'get nam/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')

    try:
      theSStack     = environment.scope_stack
      theName       = environment.operand_stack.pop() if getNamFromStk else machine.strings[multiname.nam_ix]
      theNamespace  = environment.operand_stack.pop() if getNsFromStk else machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]
      theNamespaces = [theNamespace]

      if machine.cbOnInsExe is not None:
        #machine.cbOnInsExe.MakeExtraObservation(f'tSS#{len(theSStack)}={BM.DumpVar(theSStack)}') # TODO why did I stop logging this?
        machine.cbOnInsExe.MakeExtraObservation(f'tN={BM.DumpVar(theName)}')
        machine.cbOnInsExe.MakeExtraObservation(f'tNs={BM.DumpVar(theNamespaces)}')
      object_, name, namespace, scopeStackEntry = machine.resolve_multiname(
        theSStack, # environment.scope_stack,
        theName, # stack or machine.strings[multiname.nam_ix],
        theNamespaces # [stack or machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]],
      )
    except KeyError:
      raise NotImplementedError('ReferenceError')
    else:
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'<obj> name/ns/sce=<{BM.DumpVar(object_)} type={type(object_)}> {BM.DumpVar(theName)}/{BM.DumpVar(theNamespaces)}/{BM.DumpVar(scopeStackEntry)}')

      # set property value on scopeStackEntry
      # HACK 2023-12-13 this is coded 'on a wing and a prayer'
      #if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'g_o PRE ={BM.DumpVar(machine.global_object)} IP_2 DEBUG')
      resKey = (namespace, name)
      resValue = ASPrimitive(BM.LINE(False), value)

      scopeChosen = '?'
      if isinstance(scopeStackEntry, str):
        if scopeStackEntry == "": # global scope maybe
          scopeChosen = 'global'
          machine.global_object.properties[resKey] = resValue
        else:
          if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'{BM.LINE()}: ## TODO-1 set some object\'s property . SSE is {BM.DumpVar(scopeStackEntry)}')
          assert False, f'\t{BM.LINE()}: ## TODO-1 set some object\'s property . SSE is {BM.DumpVar(scopeStackEntry)}'
      else:
        if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'{BM.LINE()}: ## TODO-2 set some object\'s property . SSE is {BM.DumpVar(scopeStackEntry)}')
        assert False, f'\t{BM.LINE()}: ## TODO-2 set some object\'s property. SSE is {BM.DumpVar(scopeStackEntry)}'

      #if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'g_o POST={BM.DumpVar(machine.global_object)} IP_3 DEBUG')
      if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'scope {scopeChosen}, ns/name {BM.DumpVar(resKey)} = {BM.DumpVar(resValue)}')

@instruction(177)
class InstanceOf(Instruction):
  pass


@instruction(178)
class IsType(Instruction):
  index: u30


@instruction(179)
class IsTypeLate(Instruction):
  pass


@instruction(16)
class Jump(Instruction):
  offset: s24
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'jump {self.offset} {strBACKWARDS_n if self.offset < 0 else ""}')
    raise ASJumpException(self.offset)


@instruction(8)
class Kill(Instruction): # … => …
  """
  Kills a local register.
  index is a u30 that must be an index of a local register.
  The local register at index is killed. It is killed by setting its value to undefined .
  """
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    assert self.index < len(environment.registers)
    environment.registers[self.index] =  RT.ASUndefined(BM.LINE(False))


@instruction(9)
class Label(Instruction):
  """
  Do nothing. Used to indicate that this location is the target of a branch.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    pass


@instruction(174)
class LessEquals(Instruction):
  pass


@instruction(173)
class LessThan(Instruction):
  pass


@instruction(27)
class LookupSwitch(Instruction): # …, index => …
  default_offset: s24
  case_offsets: Tuple[s24, ...]

  # noinspection PyMissingConstructor
  def __init__(self, reader: MemoryViewReader):
    self.default_offset = reader.read_s24()
    case_count = reader.read_int()
    self.case_offsets = read_array(reader, MemoryViewReader.read_s24, case_count + 1)


@instruction(165)
class LeftShift(Instruction):
  pass


@instruction(164)
class Modulo(Instruction):
  pass


@instruction(162)
class Multiply(Instruction):
  pass


@instruction(199)
class MultiplyInteger(Instruction):
  pass


@instruction(144)
class Negate(Instruction):
  pass


@instruction(196)
class NegateInteger(Instruction):
  pass


@instruction(87)
class NewActivation(Instruction):
  pass


@instruction(86)
class NewArray(Instruction):
  arg_count: u30


@instruction(90)
class NewCatch(Instruction):
  index: u30


@instruction(88)
class NewClass(Instruction):
    index: u30


@instruction(64)
class NewFunction(Instruction):
  index: u30


@instruction(85)
class NewObject(Instruction):
  arg_count: u30


@instruction(30)
class NextName(Instruction):
  pass


@instruction(35)
class NextValue(Instruction):
  pass


@instruction(2)
class Nop(Instruction):
  pass


@instruction(150)
class Not(Instruction): # …, value => …, !value
  """
  Boolean negation.
  Pop value off of the stack. Convert value to a Boolean using the ToBoolean algorithm (ECMA-262 section 9.2) and then negate the Boolean value.
  Push the result onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    result = not value
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(41)
class Pop(Instruction): # …, value => …
  """
  Pops the top value from the stack and discards it.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop discard<{BM.DumpVar(value)}>')


@instruction(29)
class PopScope(Instruction):
  """
  Pop a scope off of the scope stack
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.scope_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-ss.pop discard<{BM.DumpVar(value)}>')


@instruction(36)
class PushByte(Instruction): # … => …, value
  """
  Push a byte value.
  byte_value is an unsigned byte.
  The byte_value is promoted to an int, and the result is pushed onto the stack.
  """
  byte_value: u8

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = self.byte_value
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.append(value)


@instruction(47)
class PushDouble(Instruction): # … => …, value
  """
  `index` is a `u30` that must be an index into the `double` constant pool. The double value at
  `index` in the `double` constant pool is pushed onto the stack.
  """

  index: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = machine.doubles[self.index]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.append(value)


@instruction(39)
class PushFalse(Instruction): # … => …, false
  """
  Push the false value onto the stack.
  """

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    environment.operand_stack.append(False)


@instruction(45)
class PushInteger(Instruction): # … => …, value
  """
  `index` is a `u30` that must be an index into the `integer` constant pool.
  The int value at `index` in the integer constant pool is pushed onto the stack.
  """

  index: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = machine.integers[self.index]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.append(value)


@instruction(49)
class PushNamespace(Instruction):
  index: u30


@instruction(40)
class PushNaN(Instruction): # … => …, NaN
  pass


@instruction(32)
class PushNull(Instruction): # … => …, null
  """
  Push the `null` value onto the stack. Maybe use 'None' ?
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = None
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.append(value)


@instruction(48)
class PushScope(Instruction): # …, value => …
  """
  Pop value off of the stack. Push value onto the scope stack.

  >>> # 2024-01-19
  >>> inst = PushScope(PushScope.at_inst, MemoryViewReader(bytes(99)))
  >>> inst
  PushScope(opcode=48, instCodeLen=1)
  >>> myVM = avm2.vm.VirtualMachine.from_Evony() # doctest: +ELLIPSIS
  @...
  >>> callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, '')
  >>> if True or False: myVM.cbOnInsExe = callback # this activates instruction logging and extra observations
  >>> myVM # doctest: +ELLIPSIS
  VirtualMachine(traceHint='v.p:fE:...#...', class_ix=None, properties={('', 'TheMainVm'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})})
  >>> BM.DumpVar(myVM.global_object) # doctest: +ELLIPSIS
  "ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={('', 'Object'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}), ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})"
  >>> scopeStack = [myVM.global_object]
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[1]=[ASObject(traceHint='v.p:__i_:...', class_ix=None,
          properties={('', 'Object'):                ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...', class_ix=None, properties={})})]"
  >>> env = avm2.vm.MethodEnvironment.for_testing(5, scopeStack)
  >>> BM.DumpVar(env.registers) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[5]=[ASUndefined(traceHint='v.p:ft:...#0 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#1 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#2 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#3 #...', class_ix=None, properties={}),
  ASUndefined(traceHint='v.p:ft:...#4 #...', class_ix=None, properties={})]"
  >>>
  >>> # 2024-01-18
  >>> env.operand_stack.clear()
  >>> env.operand_stack.append('SomeScopeThing')
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  "[1]=['SomeScopeThing']"
  >>> inst.execute(myVM, env) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
   ai.p:MEO:...: Extra@...:-os.pop value=<'SomeScopeThing'>.
   ai.p:MEO:...: Extra@...:+ss.push value=<'SomeScopeThing'>.
  >>> BM.DumpVar(env.operand_stack) # doctest: +ELLIPSIS
  '[0]=[]'
  >>> BM.DumpVar(scopeStack) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
  "[2]=[ASObject(traceHint='v.p:__i_:...#...', class_ix=None,
          properties={('', 'Object'):                ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={}),
                      ('flash.utils', 'Dictionary'): ASObject(traceHint='v.p:__i_:...#...', class_ix=None, properties={})}),
        'SomeScopeThing']"
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    assert value is not None and value is not undefined
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+ss.push value=<{BM.DumpVar(value)}>')
    environment.scope_stack.append(value)

@instruction(37)
class PushShort(Instruction): # … => …, value
  """
  value is a u30. The value is pushed onto the stack.
  """
  value: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = self.value
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.append(value)

@instruction(44)
class PushString(Instruction): # … => …, value
  """
  index is a u30 that must be an index into the string constant pool.
  The string value at index in the string constant pool is pushed onto the stack.
  """
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = machine.strings[self.index]
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.append(value)


@instruction(38)
class PushTrue(Instruction): # … => …, true
  """
  Push the `true` value onto the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = True
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push value=<{BM.DumpVar(value)}>')
    environment.operand_stack.append(value)


@instruction(46)
class PushUnsignedInteger(Instruction):
  index: u30


@instruction(33)
class PushUndefined(Instruction):
  pass


@instruction(28)
class PushWith(Instruction):
  pass


@instruction(72)
class ReturnValue(Instruction): # …, return_value => …
  """
  Return from the currently executing method. This returns the top value on the stack.
  `return_value` is popped off of the stack, and coerced to the expected return type of the
  method. The coerced value is what is actually returned from the method.

  A `TypeError` is thrown if `return_value` cannot be coerced to the expected return type of the
  executing method.
  """

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    # FIXME: coerce to the expected return type.
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
    raise ASReturnException(value)


@instruction(71)
class ReturnVoid(Instruction): # … => …
  """
  Return from the currently executing method. This returns the value `undefined`. If the
  method has a return type, then undefined is coerced to that type and then returned.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    raise ASReturnException(undefined)


@instruction(166)
class RightShift(Instruction):
  pass


@instruction(111)
class SetGlobalSlot(Instruction):
  slot_ix: u30


@instruction(99)
class SetLocal(Instruction): # …, value => …
  """
  Set a local register.
  index is a u30 that must be an index of a local register.
  The register at index is set to value, and value is popped off the stack.
  """
  index: u30

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    assert self.index < len(environment.registers)
    environment.registers[self.index] = value


@instruction(212)
class SetLocal0(Instruction): # …, value => …
  """
  <n> = 0 is an index of a local register.
  The register at that index is set to value, and value is popped off the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    environment.registers[0] = value


@instruction(213)
class SetLocal1(Instruction): # …, value => …
  """
  <n> = 1 is an index of a local register.
  The register at that index is set to value, and value is popped off the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    environment.registers[1] = value


@instruction(214)
class SetLocal2(Instruction): # …, value => …
  """
  `<n>` = 2 is an index of a local register.
  The register at that index is set to value, and value is popped off the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    environment.registers[2] = value


@instruction(215)
class SetLocal3(Instruction): # …, value => …
  """
  <n> = 3 is an index of a local register.
  The register at that index is set to value, and value is popped off the stack.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value=<{BM.DumpVar(value)}>')
    environment.registers[3] = value


@instruction(97)
class SetProperty(Instruction): # …, obj, [ns], [name], value => …
  """
  value is the value that the property will be set to. value is popped off the stack and saved.

  index is a u30 that must be an index into the multiname constant pool. If the multiname at
  that index is a runtime multiname the name and/or namespace will also appear on the stack
  so that the multiname can be constructed correctly at runtime.

  The property with the name specified by the multiname will be resolved in obj, and will be
  set to value. If the property is not found in obj, and obj is dynamic then the property will be
  created and set to value. See “Resolving multinames” on page 10

  [Adobe ActionScript Virtual Machine 2 (AVM2)].
  """
  index: u30
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}. BTW i={self.index} OS={environment.operand_stack}')
    print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}.{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_code.co_firstlineno}. BTW i={self.index}', file=sys.stderr)

    # TODO is it a runtime multiname?
    # cf FindPropStrict for some ideas

    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'@{BM.LINE()} ## TODO use findpropstrict for logic for name & ns from stack')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'
    isMultinameRuntimeName = False # Add code to determine Name
    isMultinameRuntimeNS = False # Add code to determine Namespace

    if isMultinameRuntimeName:
      theName = environment.operand_stack.pop()

    if isMultinameRuntimeNS:
      theNS = environment.operand_stack.pop()

    theObj = environment.operand_stack.pop()
    # TODO set theObj property to value

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(109)
class SetSlot(Instruction):
  slot_ix: u30


@instruction(5)
class SetSuper(Instruction):
  index: u30

  def PlaceHolder():
    multiname = None
    getNamFromStk = multiname.getNameFromStack()
    getNsFromStk = multiname.getNamespaceFromStack()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'multi={BM.DumpVar(multiname)} n/ns from stack={BM.DumpVar(getNamFromStk)}/{BM.DumpVar(getNsFromStk)}')
    assert False, f'\t{BM.LINE()}: ## TODO use findpropstrict for logic for name & ns from stack'

@instruction(172)
class StrictEquals(Instruction):
  pass


@instruction(161)
class Subtract(Instruction):
  pass


@instruction(198)
class SubtractInteger(Instruction): # …, value1, value2 => …, value3
  """
  Pop `value1` and `value2` off of the stack and convert `value1` and `value2` to int to create
  `value1_int` and `value2_int`. Subtract `value2_int` from `value1_int`. Push the result onto the
  stack.
  """

  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_2=<{BM.DumpVar(value_2)}>')
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'-os.pop value_1=<{BM.DumpVar(value_1)}>')
    result = int(value_1) - int(value_2)
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'+os.push result=<{BM.DumpVar(result)}>')
    environment.operand_stack.append(result)


@instruction(43)
class Swap(Instruction): # …, value1, value2 => …, value2, value1
  """
  Swap the top two values on the stack. Pop value2 and value1. Push value2, then push value1.
  """
  def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
    value_2 = environment.operand_stack.pop()
    value_1 = environment.operand_stack.pop()
    if machine.cbOnInsExe is not None: machine.cbOnInsExe.MakeExtraObservation(f'{BM.DumpVar(value_1)} <=> <{BM.DumpVar(value_2)}>')
    environment.operand_stack.append(value_2)
    environment.operand_stack.append(value_1)


@instruction(3)
class Throw(Instruction):
  pass


@instruction(149)
class TypeOf(Instruction):
  pass


@instruction(167)
class UnsignedRightShift(Instruction):
  pass

if __name__ == '__main__':  # 2024-01-18 # when you run 'python thisModuleName.py' ...
  import doctest, os, sys
  # vvvv use BM.LINE() in other modules (after 'import BrewMaths as BM')
  print(f'@{BM.LINE()} ### run embedded unit tests via \'python ' + os.path.basename(__file__) + '\'')
  if False and True: # 'and' = not verbose; 'or' = verbose
    res = doctest.testmod(verbose=True) # then the tests in block comments will run. nb or testmod(verbose=True)
  else:
    res = doctest.testmod() # then the tests in block comments will run. nb or testmod(verbose=True)
  #emoji = '\u263a \U0001f60a' if res.failed == 0 else '\u2639 \U0001f534' # smily + yellow smiley if passed else sad + red
  emoji = '\u2639 \U0001f534' if res.failed else '\u263a \U0001f7e2' # sad + red if failed else smily and green
  print(f'@{BM.LINE()} ### BTW res = <{res}>, res.failed=<{res.failed}> {"!"*res.failed} {emoji}')
  sys.exit(res.failed) # return number of failed tests
