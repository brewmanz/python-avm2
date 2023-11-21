from typing import Iterable, List

import BrewMaths as BM

from avm2.abc.instructions import Instruction, read_instruction
from avm2.abc.types import ABCFile, ASMethodBody
from avm2.io import MemoryViewReader

import inspect
import logging

gDebugLevel = logging.WARNING # DEBUG, INFO, WARNING, ERROR, CRITICAL # import logging

def BuildColourNameLookup():
  global g_ColourNameLookupFromNumber
  g_ColourNameLookupFromNumber = dict()
  namNum = {
         "black":0,
         "blue":255,
         "green":32768,
         "gray":8421504,
         "silver":12632256,
         "lime":65280,
         "olive":8421376,
         "white":16777215,
         "yellow":16776960,
         "maroon":8388608,
         "navy":128,
         "red":16711680,
         "purple":8388736,
         "teal":32896,
         #"fuchsia":16711935,
         "aqua":65535,
         "magenta":16711935,
         "cyan":65535,
         "halogreen":8453965,
         "haloblue":40447,
         "haloorange":16758272,
         "halosilver":11455193
        }
  for k, v in namNum.items(): # 'reverse' dictionary
    g_ColourNameLookupFromNumber[v] = k

def DumpAttribute(item: object, attrNam: str, indent: int) -> str:
    #print(f'{" "*indent}@@10@ [{attrNam}]:{indent}')
    att = getattr(item, attrNam)
    typStr = type(att).__name__
    cls = att.__class__
    clsStr = att.__class__.__name__
    # print(f'{" "*indent}@@13@ type(att)={type(att)}')
    # voluminous # print(f'{" "*indent}@@14@ att={att}')
    # print(f'{" "*indent}@@15@ dir(type(att))={dir(type(att))}')

    if typStr == '': attStr = f'= @{BM.LINE()} !!22!attrNam=<{attrNam}>!att=<{att}>!'
    elif typStr == 'int': attStr = f'= {att}'
    elif typStr == 'list':
      lenAtt = len(att)
      attStr = f'#{lenAtt}'
      if lenAtt > 0:
        attStr += f'; final type={type(att[lenAtt-1])}'

    elif typStr == 'ASConstantPool':
      if typStr == clsStr:
        print(f'{" "*indent}[{attrNam}]:{typStr}=')
      else:
        print(f'{" "*indent}[{attrNam}]:{typStr}/{clsStr}=')
      #print(f'$$18$$ dir={dir(att)}')
      subDro = dir(att)
      for subNam in subDro:
        if subNam[:2] == '__' or subNam[-2:] == '__': continue
        DumpAttribute(att, subNam, indent+1)
      return
    elif typStr == 'method-wrapper': attStr = f'= {attrNam}'
    elif typStr == 'type': attStr = f'= {attrNam}'
    elif typStr == 'builtin_function_or_method': attStr = f'= {attrNam}'
    elif typStr == 'str':
      attStr = f'= {att}'
      if len(attStr) > 20: attStr = attStr[:18] + '..'
    else: attStr = f'= @{BM.LINE()} ??25?? typStr=<{typStr}> attrNam=<{attrNam}> att=<{att}>'

    if typStr == clsStr:
      print(f'{" "*indent}[{attrNam}]:{typStr} {attStr}')
    else:
      print(f'{" "*indent}[{attrNam}]:{typStr}/{clsStr} {attStr}')
    #if typStr == 'ASConstantPool' :
    #  sys.exit(-97)

    global g_ColourNameLookupFromNumber
    global g_cp_list_strings
    # maybe dump first & last 5
    if typStr == 'list':
      print(f'@{BM.LINE()} $$attrNam=[{attrNam}] att=[{f"{att}"[:120]}]')
      with open(f'list_{attrNam}.$txt', "w") as fTxt:
        for ix in range(len(att)):
          val = att[ix]
          strVal = f'{val}'
          lenLim = 220
          if len(strVal) > lenLim: strVal = strVal[:lenLim-2] + '..'
          fTxt.write(strVal) # actual value, up to length lenLim
          # do we want some comments?
          if False: pass
          elif attrNam == 'integers':
            fTxt.write(f' # {hex(val)}') # add hex. Colours = x RED GRN BLU
            if val in g_ColourNameLookupFromNumber:
              fTxt.write(f' # {g_ColourNameLookupFromNumber[val]}') # add colour name
          elif attrNam == 'namespaces' and val != None:
            ix = val.name_index
            fTxt.write(f' # n[ix]> {g_cp_list_strings[ix]}') # convert ns# to string value

          fTxt.write('\n') # end line
          if ix > 4 and ix < (len(att) - 5): continue
          print(f'{" "*(indent+2)}[{ix}]«{strVal}»')

def DumpAttributes(item: object, title: str, detail: int) -> str:
  print(f'## @{BM.LINE()} $$31$$ title:{title}, dir={dir(item)}')
  dro = dir(item)
  # for it in dr if it[:2] != '__' and it[-2:] != '__' :
  for nam in dro :
    if detail < 5:
      if nam[:2] == '__' or nam[-2:] == '__': continue
    indent = 1; DumpAttribute(item, nam, indent)

def test_abc_file_EvonyClient_1922(abc_file_EvonyClient_N: ABCFile):
    abc_file_EvonyClient: ABCFile = abc_file_EvonyClient_N # TODO fix HACK
    print(f'## @{BM.LINE()} being run ##')
    BuildColourNameLookup()

    print(f'## @{BM.LINE()} grab various constant_pool value ...')
    global g_cp_list_strings; g_cp_list_strings = abc_file_EvonyClient.constant_pool.strings
    print(f'## @{BM.LINE()} len(g_cp_list_strings)={len(g_cp_list_strings)}')

    if gDebugLevel <= logging.INFO:
      print(f'## @{BM.LINE()} about to DmpAtts c_p...')
      DumpAttributes(type(getattr(abc_file_EvonyClient, 'constant_pool')).__name__, f'--==-- class name??', 99)
      print(f'## @{BM.LINE()} about to DmpAtts a_f_EC...')
      DumpAttributes(abc_file_EvonyClient, f'--==-- abc_file_EvonyClient', 0)
    else:
      print(f'## @{BM.LINE()} (skipping various DmpAtts)')

    print(f'--==--')

    assert abc_file_EvonyClient.major_version == 46
    assert abc_file_EvonyClient.minor_version == 16

    #assert len(abc_file_EvonyClient.constant_pool) == 7 # TypeError: object of type 'ASConstantPool' has no len() #
    assert len(abc_file_EvonyClient.constant_pool.integers) == 44 # 463
    assert len(abc_file_EvonyClient.constant_pool.unsigned_integers) == 1 # 27
    assert len(abc_file_EvonyClient.constant_pool.doubles) == 17 # 376
    assert len(abc_file_EvonyClient.constant_pool.strings) == 2234 # 38136
    assert len(abc_file_EvonyClient.constant_pool.namespaces) == 240 # 9048
    assert len(abc_file_EvonyClient.constant_pool.ns_sets) == 49 # 1406
    assert len(abc_file_EvonyClient.constant_pool.multinames) == 1696 # 38608

    assert len(abc_file_EvonyClient.methods) == 1214 # 35243
    assert len(abc_file_EvonyClient.metadata) == 1 # 196
    assert len(abc_file_EvonyClient.instances) == 97 # 3739
    assert len(abc_file_EvonyClient.classes) == 97 # 3739
    assert len(abc_file_EvonyClient.scripts) == 87 # 3720
    assert len(abc_file_EvonyClient.method_bodies) == 859 # 34687

    assert len(read_method_body(abc_file_EvonyClient.method_bodies[0])) == 1 # 103
    assert len(read_method_body(abc_file_EvonyClient.method_bodies[1])) == 7 # 69
    assert len(read_method_body(abc_file_EvonyClient.method_bodies[2])) == 1 # 69


def read_method_body(method_body: ASMethodBody) -> List[Instruction]:
    return list(read_instructions(MemoryViewReader(method_body.code)))


def read_instructions(reader: MemoryViewReader) -> Iterable[Instruction]:
    while not reader.is_eof():
        yield read_instruction(reader)
