from typing import Iterable, List

import BrewMaths as BM
import tests.helper_abc as HA

from avm2.abc.instructions import Instruction, read_instruction
from avm2.abc.types import ABCFile, ASMethodBody
import avm2.abc.types as AT
from avm2.abc.enums import NamespaceKind
from avm2.io import MemoryViewReader
from datetime import datetime

import inspect
import logging

DEBUG = True or False # toggle and/or
gDebugLevel = logging.INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL # import logging

def test_THA2010_file_Dump_Heroes_InstanceTraits(abc_file_heroes: ABCFile):
    abc_file: ABCFile = abc_file_heroes # TODO fix HACK
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    print(f'## @{BM.LINE()} gDebugLevel={gDebugLevel} (D={logging.DEBUG}, I={logging.INFO}, W={logging.WARNING})')

    # add name strings from name indices
    abc_file.propagateStrings(BM.LINE(False))

    nInstances = len(abc_file.instances)
    n = 0
    nT = 0
    for ix in range(nInstances):
      item = abc_file.instances[ix]
      nTraits = len(item.traits)
      if nTraits:
        print(f'@{BM.LINE()}{BM.TERM_CYN()}+{n} inst[{ix}]/{nInstances} traits#{nTraits} name={item.nam_name}{BM.TERM_RESET()}')
        n += 1
        for ixT in range(nTraits):
          itemT = item.traits[ixT]
          print(f'@{BM.LINE()} +{ixT} {itemT}')
          assert isinstance(itemT, AT.ASTraitBis), f'fix this; type(itemT)={type(itemT)}'
          if nT > 99: assert 1==2, 'TODO add more lines'
          nT += 1

def test_THA2000_file_Dump_Heroes(abc_file_heroes: ABCFile):
    abc_file: ABCFile = abc_file_heroes # TODO fix HACK
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    print(f'## @{BM.LINE()} gDebugLevel={gDebugLevel} (D={logging.DEBUG}, I={logging.INFO}, W={logging.WARNING})')

    # add name strings from name indices
    abc_file.propagateStrings(BM.LINE(False))

    HA.BuildColourNameLookup()
    HA.BuildSymbolsLookup()

    print(f'## @{BM.LINE()} grab various constant_pool value ...')
    global g_cp; g_cp = abc_file.constant_pool
    global g_cp_list_strings; g_cp_list_strings = abc_file.constant_pool.strings
    print(f'## @{BM.LINE()} len(g_cp_list_strings)={len(g_cp_list_strings)}')

    print(f'## @{BM.LINE()} about to DmpAtts c_p constant_pool ASConstantPool __name__ ...')
    if gDebugLevel <= logging.DEBUG:
      HA.DumpAttributes('He', type(getattr(abc_file, 'constant_pool')).__name__, f'--==-- class name??', '', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')
    print(f'## @{BM.LINE()} about to DmpAtts c_p constant_pool ASConstantPool ...')
    if gDebugLevel <= logging.INFO:
      HA.DumpAttributes('He', type(getattr(abc_file, 'constant_pool')), f'--==-- class name??', 'cp+_', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')

    print(f'## @{BM.LINE()} about to DmpAtts a_f_EC abc_file...')
    if gDebugLevel <= logging.INFO:
      HA.DumpAttributes('He', abc_file, f'--==-- abc_file', '', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')

    print(f'--==--')

def test_THA1000_abc_file_heroes(abc_file_heroes: ABCFile):
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
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
