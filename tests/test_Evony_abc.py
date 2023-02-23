from typing import Iterable, List

from avm2.abc.instructions import Instruction, read_instruction
from avm2.abc.types import ABCFile, ASMethodBody
from avm2.io import MemoryViewReader

import inspect


def test_abc_file_EvonyClient_1922(abc_file_EvonyClient_N: ABCFile):
    abc_file_EvonyClient: ABCFile = abc_file_EvonyClient_N # TODO fix HACK
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')

    dro = dir(abc_file_EvonyClient)
    print(dro)
    print(f'--==-- abc_file_EvonyClient')
    # for it in dr if it[:2] != '__' and it[-2:] != '__' :
    for nam in dro :
      if nam[:2] == '__' or nam[-2:] == '__': continue
      att = getattr(abc_file_EvonyClient, nam)
      typStr = type(att).__name__
      if typStr == '' : attStr = '= !!!'
      elif typStr == 'int' : attStr = f'= {att}'
      elif typStr == 'list' : attStr = f'#{len(att)}'
      else: attStr = f'= ???'
      print(f'[{nam}]:{typStr} {attStr}')

    dro = dir(abc_file_EvonyClient.constant_pool)
    print(dro)
    print(f'--==-- abc_file_EvonyClient.constant_pool')
    # for it in dr if it[:2] != '__' and it[-2:] != '__' :
    for nam in dro :
      if nam[:2] == '__' or nam[-2:] == '__': continue
      att = getattr(abc_file_EvonyClient.constant_pool, nam)
      typStr = type(att).__name__
      if typStr == '' : attStr = '= !!!'
      elif typStr == 'int' : attStr = f'= {att}'
      elif typStr == 'list' : attStr = f'#{len(att)}'
      else: attStr = f'= ???'
      print(f'[{nam}]:{typStr} {attStr}')

    dro = dir(abc_file_EvonyClient.constant_pool.doubles)
    print(dro)
    print(f'--==-- abc_file_EvonyClient.constant_pool.doubles')
    # for it in dr if it[:2] != '__' and it[-2:] != '__' :
    for nam in dro :
      if nam[:2] == '__' or nam[-2:] == '__': continue
      att = getattr(abc_file_EvonyClient.constant_pool.doubles, nam)
      typStr = type(att).__name__
      if typStr == '' : attStr = '= !!!'
      elif typStr == 'int' : attStr = f'= {att}'
      elif typStr == 'list' : attStr = f'#{len(att)}'
      else: attStr = f'= ???'
      print(f'[{nam}]:{typStr} {attStr}')

    print(f'--==--')

    assert abc_file_EvonyClient.major_version == 46
    assert abc_file_EvonyClient.minor_version == 16

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
