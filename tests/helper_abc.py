from typing import Iterable, List

import BrewMaths as BM

from avm2.abc.abc_instructions import Instruction, read_instruction
from avm2.abc.abc_types import ABCFile, ASMethodBody, ASMultiname, ASNamespace, ASNamespaceBis
from avm2.abc.abc_enums import NamespaceKind
from avm2.io import MemoryViewReader
from datetime import datetime

import inspect
import logging

gDebugLevel = logging.INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL # import logging

def BuildSymbolsLookup(): # global g_SymbolsLookupFromNumber from 'data/BryanHomeGamesEvonyCachstuffSwfMainflash/symbols.csv'
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

def BuildColourNameLookup(): # global g_ColourNameLookupFromNumber from internal code
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

def DumpAttribute(project: str, item: object, attrNam: str, attrPrefix: str, indent: int) -> str: # also write *.$txt file
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
    elif attrNam == 'cbNotifications': attStr = f'= {typNam}' # can be None, unless set (!)
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
        DumpAttribute(project, att, subNam, 'cp_', indent+1)
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
      dictTrait = dict()
      fn = f'list_{project}_{attrPrefix}{attrNam}.$txt'
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

          # do we have Traits? If so, create an extra dictionary for them
          if False: pass
          elif attrNam == 'classes':
            for ixT in range(len(val.traits)):
              keyT = f'{attrNam}#{ix:03}#{ixT:02}#{val.nam_name}'
              #valT = f'{val.traits[ixT]}'
              dictTrait[keyT] = val.traits[ixT] # valT

          if ix > 4 and ix < (len(att) - 5): continue
          print(f'{" "*(indent+2)}[{ix}]«{strVal}»')

      # WAIT! Do we have any Traits to write out
      if len(dictTrait):
        fn = f'list_{project}_{attrPrefix}{attrNam}_traits.$txt'
        with open(fn, "w") as fTxt:
          print(f'@{BM.LINE()} {BM.TERM_WHT_ON_GRN()}$$attrPref/Nam=[{attrPrefix}/{attrNam}] Traits{BM.TERM_RESET()}')
          ix = 0
          for key in sorted(dictTrait):
            val = dictTrait[key]
            strVal = f'[{key}]={val.nam_name}' # = f'[{key}]={val}'
            lenLim = 1023 # 220
            if len(strVal) > lenLim: strVal = strVal[:lenLim-2] + '..'
            fTxt.write(strVal) # actual value, up to length lenLimT

            # do we want some comments?
            if ix == 0:
              fTxt.write(f' # {datetime.now()} attrNam={attrNam} fn={fn} @{BM.LINE(False)}') # add timestamp, fn, etc

            fTxt.write('\n') # end line
            ix += 1

def DumpAttributes(project: str, item: object, title: str, prefix: str, detail: int) -> str: # and call DumpAttribute
  print(f'## @{BM.LINE()} $$31$$ title:{title}, prefix:{prefix}, dir={dir(item)}')
  dir_i = dir(item)
  # for it in dir_i if it[:2] != '__' and it[-2:] != '__' :
  for nam in dir_i :
    if detail < 5:
      if nam[:2] == '__' or nam[-2:] == '__': continue
    indent = 1; DumpAttribute(project, item, nam, prefix, indent)

