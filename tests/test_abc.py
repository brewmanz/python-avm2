from typing import Iterable, List

from avm2.abc.instructions import Instruction, read_instruction
from avm2.abc.types import ABCFile, ASMethodBody
from avm2.io import MemoryViewReader

import inspect

DEBUG = True or False # toggle and/or



def test_abc_file_heroes(abc_file_heroes: ABCFile):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    print(f'--==--')

    dro = dir(abc_file_heroes)
    print(dro)
    print(f'--==-- abc_file_heroes')

    # for it in dr if it[:2] != '__' and it[-2:] != '__' :
    for nam in dro :
      if nam[:2] == '__' or nam[-2:] == '__': continue
      att = getattr(abc_file_heroes, nam)
      typStr = type(att).__name__
      if typStr == '' : attStr = '= !!!'
      elif typStr == 'int' : attStr = f'= {att}'
      elif typStr == 'list' : attStr = f'#{len(att)}'
      else: attStr = f'= ???'

      print(f'[{nam}]:{typStr} {attStr}')


    print(f'--==--')

    # dc = abc_file_heroes.__dict__
    # print(dc)

    assert abc_file_heroes.major_version == 46
    assert abc_file_heroes.minor_version == 16
    assert len(abc_file_heroes.constant_pool.integers) == 463
    assert len(abc_file_heroes.constant_pool.unsigned_integers) == 27
    assert len(abc_file_heroes.constant_pool.doubles) == 376
    assert len(abc_file_heroes.constant_pool.strings) == 38136
    assert len(abc_file_heroes.constant_pool.namespaces) == 9048
    assert len(abc_file_heroes.constant_pool.ns_sets) == 1406
    assert len(abc_file_heroes.constant_pool.multinames) == 38608
    assert len(abc_file_heroes.methods) == 35243
    assert len(abc_file_heroes.metadata) == 196
    assert len(abc_file_heroes.instances) == 3739
    assert len(abc_file_heroes.classes) == 3739
    assert len(abc_file_heroes.scripts) == 3720
    assert len(abc_file_heroes.method_bodies) == 34687

    assert len(read_method_body(abc_file_heroes.method_bodies[0])) == 103
    assert len(read_method_body(abc_file_heroes.method_bodies[1])) == 69
    assert len(read_method_body(abc_file_heroes.method_bodies[2])) == 69


def read_method_body(method_body: ASMethodBody) -> List[Instruction]:
    return list(read_instructions(MemoryViewReader(method_body.code)))


def read_instructions(reader: MemoryViewReader) -> Iterable[Instruction]:
    while not reader.is_eof():
        yield read_instruction(reader)
