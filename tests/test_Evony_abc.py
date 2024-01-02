from typing import Iterable, List

import BrewMaths as BM
import tests.helper_abc as HA

from avm2.abc.instructions import Instruction, read_instruction
from avm2.abc.types import ABCFile, ASMethodBody, ASMultiname, ASNamespace, ASNamespaceBis
import avm2.abc.types as AT
from avm2.abc.enums import NamespaceKind
from avm2.io import MemoryViewReader
from datetime import datetime

import inspect
import logging

gDebugLevel = logging.INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL # import logging

class Object(object):
  pass

def test_TEA2100_CheckAddingFieldToDataclass():
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    listStrings = (None
    , 'flash.utils'
    , 'Dictionary'
    , ''
    , 'void'
    , 'Object'
    , 'int'
    , 'flash.display'
    , 'DisplayObject')

    asnamespace_kind8_nameindex4 = b'\x08\x07'

    mvr = MemoryViewReader(asnamespace_kind8_nameindex4)
    assert mvr.read_u8() == 0x08
    assert mvr.read_int() == 0x07

    mvr = MemoryViewReader(asnamespace_kind8_nameindex4)
    asns = ASNamespace(mvr);
    assert asns.kind == NamespaceKind.NAMESPACE
    assert asns.nam_ix == 7 # flash.display
    print(f'## @{BM.LINE()} asns={asns}.')
    assert f'{asns}' == 'ASNamespace(kind=<NamespaceKind.NAMESPACE: 8>, nam_ix=7)'

    asns.justAssignName = 'justAssignedName' # does NOT do what's needed
    print(f'## @{BM.LINE()} asns={asns}.')
    assert f'{asns.justAssignName}' == 'justAssignedName' # kinda good but ..
    assert f'{asns}' == 'ASNamespace(kind=<NamespaceKind.NAMESPACE: 8>, nam_ix=7)' # .. no good for me
    # 'ASNamespace' object has no attribute 'repr' # assert f'{asns.repr()}' == 'AS...' # .. no good for me
    # 'ASNamespace' object has no attribute 'str' # assert f'{asns.str()}' == 'AS...' # .. no good for me

    setattr(asns, 'setAttrName', 'setAttredName')
    print(f'## @{BM.LINE()} asns={asns}.')
    assert f'{asns.setAttrName}' == 'setAttredName' # kinda good but ..
    assert f'{asns}' == 'ASNamespace(kind=<NamespaceKind.NAMESPACE: 8>, nam_ix=7)' # .. no good for me

    # OK, so try a derived class ...
    pseudoConstPool = Object()
    pseudoConstPool.strings = listStrings
    print(f'## @{BM.LINE()} pseudoConstPool={pseudoConstPool}.')
    #asnsBis = ASNamespaceBis(asns, listStrings, 123)
    asnsBis = ASNamespaceBis(asns, pseudoConstPool, 123)
    print(f'## @{BM.LINE()} asnsBis={asnsBis}.')
    # note that the name of the 'name' field might vary e.g. maybe 'nameStr' or 'strName'
    #assert f'{asnsBis}'.startswith("ASNamespaceBis(kind=<NamespaceKind.NAMESPACE: 8>, nam_ix=7, ")
    #assert f'{asnsBis}'.endswith("='flash.display')")
    assert f'{asnsBis}' == "ASNamespaceBis(kind=<NamespaceKind.NAMESPACE: 8>, nam_ix=7, ixCP=123, nam_name='flash.display')"

def test_TEA2014_file_Dump_EvonyClient_MethodBodiesTraits(abc_file_EvonyClient_N: ABCFile):
    abc_file: ABCFile = abc_file_EvonyClient_N # TODO fix HACK
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    print(f'## @{BM.LINE()} gDebugLevel={gDebugLevel} (D={logging.DEBUG}, I={logging.INFO}, W={logging.WARNING})')

    # add name strings from name indices
    abc_file.propagateStrings(BM.LINE(False))

    nItems = len(abc_file.method_bodies)
    n = 0
    nT = 0
    for ix in range(nItems):
      item = abc_file.method_bodies[ix]
      nTraits = len(item.traits)
      if nTraits:
        print(f'@{BM.LINE()}{BM.TERM_CYN()}+{n} method_bodies[{ix}]/{nItems} traits#{nTraits} name={item.nam_name}{BM.TERM_RESET()}')
        n += 1
        for ixT in range(nTraits):
          itemT = item.traits[ixT]
          print(f'@{BM.LINE()} +{ixT} {itemT}')
          assert isinstance(itemT, AT.ASTraitBis), f'fix this; type(itemT)={type(itemT)}'
          if nT > 99: assert 1==2, 'TODO add more lines'
          nT += 1
def test_TEA2012_file_Dump_EvonyClient_ClassTraits(abc_file_EvonyClient_N: ABCFile):
    abc_file: ABCFile = abc_file_EvonyClient_N # TODO fix HACK
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    print(f'## @{BM.LINE()} gDebugLevel={gDebugLevel} (D={logging.DEBUG}, I={logging.INFO}, W={logging.WARNING})')

    # add name strings from name indices
    abc_file.propagateStrings(BM.LINE(False))

    nItems = len(abc_file.classes)
    n = 0
    nT = 0
    for ix in range(nItems):
      item = abc_file.classes[ix]
      nTraits = len(item.traits)
      if nTraits:
        print(f'@{BM.LINE()}{BM.TERM_CYN()}+{n} class[{ix}]/{nItems} traits#{nTraits} name={item.nam_name}{BM.TERM_RESET()}')
        n += 1
        for ixT in range(nTraits):
          itemT = item.traits[ixT]
          print(f'@{BM.LINE()} +{ixT} {itemT}')
          assert isinstance(itemT, AT.ASTraitBis), f'fix this; type(itemT)={type(itemT)}'
          if nT > 99: assert 1==2, 'TODO add more lines'
          nT += 1
def test_TEA2010_file_Dump_EvonyClient_InstanceTraits(abc_file_EvonyClient_N: ABCFile):
    abc_file: ABCFile = abc_file_EvonyClient_N # TODO fix HACK
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    print(f'## @{BM.LINE()} gDebugLevel={gDebugLevel} (D={logging.DEBUG}, I={logging.INFO}, W={logging.WARNING})')

    # add name strings from name indices
    abc_file.propagateStrings(BM.LINE(False))

    nItems = len(abc_file.instances)
    n = 0
    nT = 0
    for ix in range(nItems):
      item = abc_file.instances[ix]
      nTraits = len(item.traits)
      if nTraits:
        print(f'@{BM.LINE()}{BM.TERM_CYN()}+{n} inst[{ix}]/{nItems} traits#{nTraits} name={item.nam_name}{BM.TERM_RESET()}')
        n += 1
        for ixT in range(nTraits):
          itemT = item.traits[ixT]
          print(f'@{BM.LINE()} +{ixT} {itemT}')
          assert isinstance(itemT, AT.ASTraitBis), f'fix this; type(itemT)={type(itemT)}'
          if nT > 99: assert 1==2, 'TODO add more lines'
          nT += 1


def test_TEA2000_file_Dump_EvonyClient_1922(abc_file_EvonyClient_N: ABCFile):
    abc_file: ABCFile = abc_file_EvonyClient_N # TODO fix HACK
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
      HA.DumpAttributes('Ev', type(getattr(abc_file, 'constant_pool')).__name__, f'--==-- class name??', '', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')
    print(f'## @{BM.LINE()} about to DmpAtts c_p constant_pool ASConstantPool ...')
    if gDebugLevel <= logging.INFO:
      HA.DumpAttributes('Ev', type(getattr(abc_file, 'constant_pool')), f'--==-- class name??', 'cp+_', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')

    print(f'## @{BM.LINE()} about to DmpAtts a_f_EC abc_file...')
    if gDebugLevel <= logging.INFO:
      HA.DumpAttributes('Ev', abc_file, f'--==-- abc_file', '', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')

    print(f'--==--')

def test_TEA1000_file_EvonyClient_1922(abc_file_EvonyClient_N: ABCFile):
    abc_file: ABCFile = abc_file_EvonyClient_N # TODO fix HACK

    assert abc_file.major_version == 46
    assert abc_file.minor_version == 16

    #assert len(abc_file.constant_pool) == 7 # TypeError: object of type 'ASConstantPool' has no len() #
    assert len(abc_file.constant_pool.integers) == 44 # 463
    assert len(abc_file.constant_pool.unsigned_integers) == 1 # 27
    assert len(abc_file.constant_pool.doubles) == 17 # 376
    assert len(abc_file.constant_pool.strings) == 2234 # 38136
    assert len(abc_file.constant_pool.namespaces) == 240 # 9048
    assert len(abc_file.constant_pool.ns_sets) == 49 # 1406
    assert len(abc_file.constant_pool.multinames) == 1696 # 38608

    assert len(abc_file.methods) == 1214 # 35243
    assert len(abc_file.metadata) == 1 # 196
    assert len(abc_file.instances) == 97 # 3739
    assert len(abc_file.classes) == 97 # 3739
    assert len(abc_file.scripts) == 87 # 3720
    assert len(abc_file.method_bodies) == 859 # 34687

    assert len(read_method_body(abc_file.method_bodies[0])) == 1 # 103
    assert len(read_method_body(abc_file.method_bodies[1])) == 7 # 69
    assert len(read_method_body(abc_file.method_bodies[2])) == 1 # 69


def read_method_body(method_body: ASMethodBody) -> List[Instruction]:
    return list(read_instructions(MemoryViewReader(method_body.code)))

def read_instructions(reader: MemoryViewReader) -> Iterable[Instruction]:
    while not reader.is_eof():
        yield read_instruction(reader)
