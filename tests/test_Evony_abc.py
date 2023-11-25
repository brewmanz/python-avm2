from typing import Iterable, List

import BrewMaths as BM

from avm2.abc.instructions import Instruction, read_instruction
from avm2.abc.types import ABCFile, ASMethodBody, ASMultiname, ASNamespace, ASNamespaceBis
from avm2.abc.enums import NamespaceKind
from avm2.io import MemoryViewReader
from datetime import datetime

import inspect
import logging

gDebugLevel = logging.INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL # import logging

def BuildSymbolsLookup():
  # int;str matches swf/MainFlash/sprites/DefineSprite_ numbers and strings
  global g_SymbolsLookupFromNumber
  g_SymbolsLookupFromNumber = dict()
  with open(f'data/BryanHomeGamesEvonyCachstuffSwfMainflash/symbols.csv', 'r') as fCsv:
    strLines = fCsv.readlines()
  with open(f'dict_symbols.$txt', 'w') as fTxt:
    fTxt.writelines(strLines)
  kMin = 99999; kMax = -1
  for strLine in strLines:
    frags = strLine.strip().split(';')
    #print(f'@{BM.LINE()} frags={frags}')
    k = int(frags[0])
    if kMin > k and k > 0: kMin = k
    if kMax < k and k > 0: kMax = k
    v = frags[1]
    g_SymbolsLookupFromNumber[k] = v
  print(f'@{BM.LINE()} g_SymbolsLookupFromNumber#={len(g_SymbolsLookupFromNumber)} from {len(strLines)} lines; kMin/Max={kMin}/{kMax}')
  if gDebugLevel <= logging.INFO:
    for k,v in g_SymbolsLookupFromNumber.items():
      if v.startswith('EvonyClient') or v.startswith('_EvonyClient') or v.startswith('com.evony.'):
        if '____' in v: continue
        if '_swf_' in v: continue
        print(f'@{BM.LINE()} [{k}] = {v}')

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

def DumpAttribute(item: object, attrNam: str, attrPrefix: str, indent: int) -> str:
    #print(f'{" "*indent}@@10@ [{attrNam}]:{indent}')
    att = getattr(item, attrNam)
    typ = type(att)
    typStr = str(typ) # att.__name__ # typStr = type(att).__name__
    typNam = typ.__name__
    cls = att.__class__
    clsStr = str(cls)
    clsNam = cls.__name__

    # print(f'@{BM.LINE()} !!!!att attrNam={attrNam} typ={typ} typStr={typStr} typNam={typNam} cls={cls} clsStr={clsStr}  clsNam={clsNam} dir(att)={dir(att)}')
    # if True: return

    # print(f'{" "*indent}@@13@ type(att)={type(att)}')
    # voluminous # print(f'{" "*indent}@@14@ att={att}')
    # print(f'{" "*indent}@@15@ dir(type(att))={dir(type(att))}')

    if typNam == '': attStr = f'= @{BM.LINE()} {BM.TERM_GRY_ON_RED()}!!22!attrNam=<{attrNam}>!att=<{att}>!{BM.TERM_RESET()}'
    elif typNam == 'int': attStr = f'= {att}'
    elif typNam == 'list':
      lenAtt = len(att)
      attStr = f'#{lenAtt}'
      if lenAtt > 0:
        attStr += f'; final type={type(att[-1])}'

    elif typNam == 'ASConstantPool':
      if typNam == clsNam:
        print(f'@{BM.LINE()}{"  "*indent}[{attrNam}]:{typNam}=')
      else:
        print(f'@{BM.LINE()}{"  "*indent}[{attrNam}]:{typNam}/{clsNam}=')
      #print(f'$$18$$ dir={dir(att)}')
      subDro = dir(att)
      for subNam in subDro:
        if subNam[:2] == '__' or subNam[-2:] == '__': continue
        DumpAttribute(att, subNam, 'cp_', indent+1)
      return
    elif typNam == 'method-wrapper': attStr = f'=mw {attrNam}'
    elif typNam == 'type': attStr = f'=t {attrNam}'
    elif typNam == 'builtin_function_or_method': attStr = f'=bifom {attrNam}'
    elif typNam == 'function': attStr = f'=fn {attrNam}'
    elif typNam == 'str':
      attStr = f"=s '{att}'"
      if len(attStr) > 20: attStr = attStr[:18] + '..'
    elif typNam == 'method': attStr = f'=m {attrNam}'
    else: attStr = f'= @{BM.LINE()} {BM.TERM_GRY_ON_RED()}??25?? !!typNam=<{typNam}>!! attrNam=<{attrNam}> att=<{att}{BM.TERM_RESET()}>'

    if typNam == clsNam:
      print(f'@{BM.LINE()}{"  "*indent}{BM.TERM_GRY_ON_BLU()}[{attrNam}]:{typNam} {attStr}{BM.TERM_RESET()}')
    else:
      print(f'@{BM.LINE()}{"  "*indent}{BM.TERM_WHT_ON_BLU()}[{attrNam}]:{typNam}/{clsNam} {attStr}{BM.TERM_RESET()}')
    #if typNam == 'ASConstantPool' :
    #  sys.exit(-97)

    global g_ColourNameLookupFromNumber
    global g_cp
    global g_cp_list_strings
    # maybe dump first & last 5

    # if True: return #########################################

    if typNam == 'list':
      if gDebugLevel <= logging.INFO:
        #print(f'@{BM.LINE()} $$att type(att)={type(att)} typNam={typNam} dir(att)={dir(att)}') # full
        print(f'@{BM.LINE()} $$att type(att)={type(att)} typNam={typNam} dir(att)={list(a for a in dir(att) if not a.startswith("__"))}') # filtered
        #print(f'@{BM.LINE()} $$att[-1] type(att{-1})={type(att[-1])} dir(att[-1])={dir(att[-1])}')  # full
        print(f'@{BM.LINE()} $$att[-1] type(att{-1})={type(att[-1])} dir(att[-1])={list(a for a in dir(att[-1]) if not a.startswith("__"))}') # filtered

      print(f'@{BM.LINE()} {BM.TERM_WHT_ON_GRN()}$$attrPref/Nam=[{attrPrefix}/{attrNam}] att=[{f"{att}"[:120]}]{BM.TERM_RESET()}')
      fn = f'list_{attrPrefix}{attrNam}.$txt'
      with open(fn, "w") as fTxt:
        for ix in range(len(att)):
          val = att[ix]
          strVal = f'{val}'
          lenLim = 1023 # 220
          if len(strVal) > lenLim: strVal = strVal[:lenLim-2] + '..'
          fTxt.write(strVal) # actual value, up to length lenLim

          # do we want some comments?
          if ix == 0:
            fTxt.write(f' # {datetime.now()} attrNam={attrNam} fn={fn} @{BM.LINE(False)}') # add timestamp, fn, etc

          if False: pass
          #elif val is ASMultiname: # seems to not trigger
          elif attrNam == 'multinamesXXX' and val != None:
            fTxt.write(f' # qn={val.qualified_name(g_cp)}') # add QN
          elif attrNam == 'integers':
            fTxt.write(f' # {hex(val)}') # add hex. Colours = x RED GRN BLU
            if val in g_ColourNameLookupFromNumber:
              fTxt.write(f' # {g_ColourNameLookupFromNumber[val]}') # add colour name
          elif False and attrNam == 'namespaces' and val != None: # obsolete with ASNamespaceBis
            ix = val.nam_ix
            fTxt.write(f' # n[ix]> {g_cp_list_strings[ix]}') # convert ns# to string value

          fTxt.write('\n') # end line
          if ix > 4 and ix < (len(att) - 5): continue
          print(f'{" "*(indent+2)}[{ix}]«{strVal}»')

def DumpAttributes(item: object, title: str, prefix: str, detail: int) -> str:
  print(f'## @{BM.LINE()} $$31$$ title:{title}, prefix:{prefix}, dir={dir(item)}')
  dir_i = dir(item)
  # for it in dir_i if it[:2] != '__' and it[-2:] != '__' :
  for nam in dir_i :
    if detail < 5:
      if nam[:2] == '__' or nam[-2:] == '__': continue
    indent = 1; DumpAttribute(item, nam, prefix, indent)

def test_CheckAddingFieldToDataclass():
    print(f'## @{BM.LINE()} being run ##')
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
    asnsBis = ASNamespaceBis(asns, listStrings, 123)
    print(f'## @{BM.LINE()} asnsBis={asnsBis}.')
    # note that the name of the 'name' field might vary e.g. maybe 'nameStr' or 'strName'
    assert f'{asnsBis}'.startswith("ASNamespaceBis(kind=<NamespaceKind.NAMESPACE: 8>, nam_ix=7, ")
    assert f'{asnsBis}'.endswith("='flash.display')")
    assert f'{asnsBis}' == "ASNamespaceBis(kind=<NamespaceKind.NAMESPACE: 8>, nam_ix=7, ixCP=123, nam_name='flash.display')"

def test_abc_file_EvonyClient_1922(abc_file_EvonyClient_N: ABCFile):
    abc_file_EvonyClient: ABCFile = abc_file_EvonyClient_N # TODO fix HACK
    print(f'## @{BM.LINE()} being run ##')
    print(f'## @{BM.LINE()} gDebugLevel={gDebugLevel} (D={logging.DEBUG}, I={logging.INFO}, W={logging.WARNING})')

    # add name strings from name indices
    abc_file_EvonyClient.constant_pool.propogateStrings()

    BuildColourNameLookup()
    BuildSymbolsLookup()

    print(f'## @{BM.LINE()} grab various constant_pool value ...')
    global g_cp; g_cp = abc_file_EvonyClient.constant_pool
    global g_cp_list_strings; g_cp_list_strings = abc_file_EvonyClient.constant_pool.strings
    print(f'## @{BM.LINE()} len(g_cp_list_strings)={len(g_cp_list_strings)}')

    print(f'## @{BM.LINE()} about to DmpAtts c_p constant_pool ASConstantPool __name__ ...')
    if gDebugLevel <= logging.DEBUG:
      DumpAttributes(type(getattr(abc_file_EvonyClient, 'constant_pool')).__name__, f'--==-- class name??', '', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')
    print(f'## @{BM.LINE()} about to DmpAtts c_p constant_pool ASConstantPool ...')
    if gDebugLevel <= logging.INFO:
      DumpAttributes(type(getattr(abc_file_EvonyClient, 'constant_pool')), f'--==-- class name??', 'cp+_', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')

    print(f'## @{BM.LINE()} about to DmpAtts a_f_EC abc_file_EvonyClient...')
    if gDebugLevel <= logging.INFO:
      DumpAttributes(abc_file_EvonyClient, f'--==-- abc_file_EvonyClient', '', 2)
    else:
      print(f'## @{BM.LINE()} (skipping that DmpAtts)')

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
