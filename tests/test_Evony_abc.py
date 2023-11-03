from typing import Iterable, List

import BrewMaths as BM

from avm2.abc.instructions import Instruction, read_instruction
from avm2.abc.types import ABCFile, ASMethodBody
from avm2.io import MemoryViewReader

import inspect

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
        attStr += f'; 1st has type {type(att[0])}'

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

    # maybe dump first & last 5
    if typStr == 'list':
      # print(f'@{BM.LINE()} att={att}')
      for ix in range(len(att)):
        if ix > 4 and ix < (len(att) - 5): continue
        strVal = f'{att[ix]}'
        lenLim = 200
        if len(strVal) > lenLim: strVal = strVal[:lenLim-2] + '..'
        print(f'{" "*(indent+2)}[{ix}]={strVal}')

def DumpAttributes(item: object, title: str, detail: int) -> str:
  print(f'## @{BM.LINE()} $$31$$ title:{title}, dir={dir(item)}')
  dro = dir(item)
  # for it in dr if it[:2] != '__' and it[-2:] != '__' :
  for nam in dro :
    if detail < 5:
      if nam[:2] == '__' or nam[-2:] == '__': continue
    indent = 1
    DumpAttribute(item, nam, indent)

def test_abc_file_EvonyClient_1922(abc_file_EvonyClient_N: ABCFile):
    abc_file_EvonyClient: ABCFile = abc_file_EvonyClient_N # TODO fix HACK
    print(f'## @{BM.LINE()} being run ##')

    DumpAttributes(type(getattr(abc_file_EvonyClient, 'constant_pool')).__name__, f'--==-- class name??', 99)
    DumpAttributes(abc_file_EvonyClient, f'--==-- abc_file_EvonyClient', 0)

    print(f'--==--')

    assert abc_file_EvonyClient.major_version == 46
    assert abc_file_EvonyClient.minor_version == 16

    assert len(abc_file_EvonyClient.constant_pool) == 7
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
