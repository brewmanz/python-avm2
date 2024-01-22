from avm2.runtime import undefined
from avm2.swf.swf_types import DoABCTag, Tag
from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
from avm2.abc.abc_instructions import CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace
import avm2.runtime as RT
import inspect, sys
import pytest
import logging
# to run selected tests # pytest -k "test_E_T1400 or test_T1400" -s
# ln -s ~/git/BDL/Games/Evony/PythonBits/MyGamesHelper.py (in git/python-avm2_AdobeSwfActionScript)
# ln -s ~/git/BDL/Games/Evony/PythonBits/BrewMaths.py (in git/python-avm2_AdobeSwfActionScript)

from pytest_check import check # pip install pytest-check

import MyGamesHelper as MGH
import BrewMaths as BM
import avm2.abc.abc_enums as EN

#from /home/bryan/git/BDL/Games/Evony/PythonBits/MyGamesHelper import MyGamesHelper as MGH

# run via 'pytest -s' (that's pytest-3), to get 'being run ##' messages

def test_TEV6000_EvC_HospitalWin_bits(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  assert 1 == 2

def test_TEV5000_EvC_toDebugString_VariousBeans(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  assert 1 == 2

def test_TEV3000_LoaderUtil_createAbsoluteURL(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')

  class_mx_utils_LoaderUtil_ix = machine_EvonyClient_N.lookup_class('mx.utils:LoaderUtil')
  assert class_mx_utils_LoaderUtil_ix == 17
  myClass = machine_EvonyClient_N.abc_file.classes[class_mx_utils_LoaderUtil_ix]

  for ixT in range(len(myClass.traits)):
    item = myClass.traits[ixT]
    print(f'@{BM.LINE()} traits[{ixT}] = {item}')

  traitName = 'createAbsoluteURL'
  myTrait = next((x for x in myClass.traits if x.nam_name == traitName), None)
  assert myTrait, f'class {myClass.nam_name}, trait <{traitName}> not found'
  print(f'@{BM.LINE()} trait = {myTrait}')
  assert myTrait.kind == EN.TraitKind.METHOD, f'class {myClass.nam_name}, trait <{traitName}> wrong kind'

  methodIx = myTrait.data.method_ix
  assert methodIx == 411, f'methodIx {methodIx} has unexpected value'
  callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100)
  machine_EvonyClient_N.cbOnInsExe = callback
  machine_EvonyClient_N.cbOnInsExe = None # Stop callback
  dummyInstance = RT.ASObject(f'@{BM.LINE(False)} dummyInstance')

  # 2024-01-00
  act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, 'param1', 'param2')
  print(f'@{BM.LINE()} act = {act}')

  # 2024-01-21

  # param1 exists, and param2 either contains colon, or starts with fwd slash or bwd slash) then ...
  # .. if param1 contains '?', then param1 is stripped of it and all following
  # .. if param1 contains '#', then param1 is stripped of it and all following
  # .. set loc5 to rightmost / or \ in param1
  # .. if param2 starts with ./ then strip off 1st 2 chars
  # .. while param2 starts with ../ then strip off 1st 3 chars and loc5 is stepped back to previous rightmost / or \ in (param1 prior to loc5)
  # .. if loc5 points to useable fwd or bwd slash in param1, then
  # .... return param1 up to and including fwd or bwd slash, plus param2
  # else return param2

  if True: # various no slash in param2
    print(f'@{BM.LINE()} ...')
    param1 = 'PARAM1'; param2 = 'param2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    #print(f'@{BM.LINE()} act = {act}')
    #check.equal(act, 'SANITYCHECK', f'@{BM.LINE()} (traitName){BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    check.equal(act, param2, f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = ''; param2 = 'param2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, param2, f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = None; param2 = 'param2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, param2, f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    # fails # param1 = undefined; param2 = 'param2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    # fails # check.equal(act, param2, f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
  if True: # various slash in param2 but no param1
    print(f'@{BM.LINE()} ...')
    param1 = ''; param2 = 'p/aram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, param2, f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = None; param2 = 'p/aram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, param2, f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = None; param2 = 'pa\\ram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, param2, f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
  if True: # colon in param2 with param1 with (nothing special) or ? or #
    print(f'@{BM.LINE()} ...')
    param1 = 'PARAM1'; param2 = 'p:aram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'p:aram2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'param1?a.b'; param2 = 'p:aram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'p:aram2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'param1#a.b'; param2 = 'p:aram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'p:aram2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'param1?a#b'; param2 = 'p:aram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'p:aram2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'param1#a?b'; param2 = 'p:aram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'p:aram2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
  if True: # / in param2 with param1 with ? or # or not
    print(f'@{BM.LINE()} ...')
    param1 = 'PARAM1'; param2 = 'par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par/am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PARAM1?a.b'; param2 = 'par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par/am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PARAM1#a.b'; param2 = 'par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par/am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PARAM1?a#b'; param2 = 'par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par/am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PARAM1#a?b'; param2 = 'par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par/am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
  if True: # \ in param2 with param1 with ? or # or not
    print(f'@{BM.LINE()} ...')
    param1 = 'PARAM1'; param2 = 'par\\am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par\\am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PARAM1?a.b'; param2 = 'par\\am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par\\am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PARAM1#a.b'; param2 = 'par\\am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par\\am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PARAM1?a#b'; param2 = 'par\\am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par\\am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PARAM1#a?b'; param2 = 'par\\am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'par\\am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
  if True: # / twice in param1 with param2 starting with ./ or ../
    print(f'@{BM.LINE()} ...')
    param1 = 'PAR/AM/1?a'; param2 = 'param2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'param2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')

    # reset callback to show code flow
    callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(200)
    machine_EvonyClient_N.cbOnInsExe = callback

    param1 = 'PAR/AM/1?a'; param2 = './param2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'PA/RA/M1/param2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')

    machine_EvonyClient_N.cbOnInsExe = None # stop callback

    param1 = 'PAR/AM/1?a'; param2 = '././par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'PA/RA/M1par/am2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PAR\\AM\\1?a'; param2 = './par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'PAR\\AM\\1/param2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PAR/AM/1?a'; param2 = '././pa/ram2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'PAR/AM/1pa/ram2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PAR/AM/1?a'; param2 = '../par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'PAR/AMparam2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')
    param1 = 'PAR/AM/1?a'; param2 = '../../par/am2';   act = machine_EvonyClient_N.call_static(methodIx, dummyInstance, param1, param2)
    check.equal(act, 'PARparam2', f'@{BM.LINE()} {traitName}({BM.DumpVar(param1)}, {BM.DumpVar(param2)}) -> {act}')

  #assert False, f'TODO @{BM.LINE(False)} LoaderUtil.createAbsoluteURL'

def test_TEV2120_InitAllClasseInstances(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  # empty # for item in machine_EvonyClient_N.class_objects:
  print(f'@{BM.LINE()} class count = {len(machine_EvonyClient_N.abc_file.classes)}')

  #bagClassNonZeroInitIx = [item.init_ix for item in filter(lambda x: x.init_ix > 0, machine_EvonyClient_N.abc_file.classes)]
  #maxClassNonZeroInitIx = max(bagClassNonZeroInitIx)
  #minClassNonZeroInitIx = min(bagClassNonZeroInitIx)
  #print(f'@{BM.LINE()} ClassNonZeroInitIx range = {minClassNonZeroInitIx} to {maxClassNonZeroInitIx}')
  bagClassInitIx = [item.init_ix for item in machine_EvonyClient_N.abc_file.classes]
  classInitIxStats = BM.NullNanZeroMinMax(bagClassInitIx)
  print(f'@{BM.LINE()} Class InitIx stats = {classInitIxStats}')

  assert len(machine_EvonyClient_N.abc_file.classes) == len(machine_EvonyClient_N.abc_file.instances), 'Sanity check'
  print(f'@{BM.LINE()} l(abc.mb)={len(machine_EvonyClient_N.abc_file.method_bodies)}')
  print(f'@{BM.LINE()} item \nC={machine_EvonyClient_N.abc_file.classes[0]} \nI={machine_EvonyClient_N.abc_file.instances[0]}')
  n = 0
  for ix in range(len(machine_EvonyClient_N.abc_file.classes)):
    itemC = machine_EvonyClient_N.abc_file.classes[ix]
    itemI = machine_EvonyClient_N.abc_file.instances[ix]
    #print(f'@{BM.LINE()} item \nC={itemC} \nI={itemI}')
    print(f'{ix}, ', end='')
    if itemI.init_ix:
      n += 1
      print(f'\n@{BM.LINE()} #{n} instances[{ix}]={itemI.nam_name} init_ix={itemI.init_ix}')
      callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100)
      machine_EvonyClient_N.cbOnInsExe = callback
      act = machine_EvonyClient_N.call_ClassClassInit(itemI.init_ix, '')
      print(f'## @{BM.LINE()} init res=<{act}>')

def test_TEV2110_InitAllClassClasses(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  # empty # for item in machine_EvonyClient_N.class_objects:
  print(f'@{BM.LINE()} class count = {len(machine_EvonyClient_N.abc_file.classes)}')
  assert len(machine_EvonyClient_N.abc_file.classes) == len(machine_EvonyClient_N.abc_file.instances), 'Sanity check'
  print(f'@{BM.LINE()} l(abc.mb)={len(machine_EvonyClient_N.abc_file.method_bodies)}')
  print(f'@{BM.LINE()} item \nC={machine_EvonyClient_N.abc_file.classes[0]} \nI={machine_EvonyClient_N.abc_file.instances[0]}')
  n = 0
  for ix in range(len(machine_EvonyClient_N.abc_file.classes)):
    itemC = machine_EvonyClient_N.abc_file.classes[ix]
    itemI = machine_EvonyClient_N.abc_file.instances[ix]
    #print(f'@{BM.LINE()} item \nC={itemC} \nI={itemI}')
    print(f'{ix}, ', end='')
    if itemC.init_ix:
      n += 1
      print(f'\n@{BM.LINE()} #{n} classes[{ix}]={itemC.nam_name} init_ix={itemC.init_ix}')
      callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100)
      machine_EvonyClient_N.cbOnInsExe = callback
      act = machine_EvonyClient_N.call_ClassInstanceInit(itemC.init_ix, '')
      print(f'## @{BM.LINE()} init res=<{act}>')


@pytest.mark.skip(reason="cannot find class com.evony.factory.ImageManager") # import pytest
def test_TEV2000_EvC_ImageManager_initAllianceLevelMap(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')

  ixClass = machine_EvonyClient_N.lookup_class('com.evony.factory.ImageManager')
  assert ixClass == -1
  ixMethod = machine_EvonyClient_N.lookup_method('com.evony.factory.ImageManager.initAllianceLevelMap')
  assert ixMethod == -1

  # private function initAllianceLevelMap() : void
  item = Object()
  print(f'@{BM.LINE()} item={item}')
  assert machine_EvonyClient_N.call_method('com.evony.factory.ImageManager.initAllianceLevelMap', item) == None
  print(f'@{BM.LINE()} item={item}')

  assert 'check' == f'output @{BM.LINE()}'

def test_TEV0100_EvC_SomeSizeInfo(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  print(f'@{BM.LINE()} l(abc.mb)={len(machine_EvonyClient_N.abc_file.method_bodies)} l(m2b)={len(machine_EvonyClient_N.method_to_body)}')
  #print(f'@{BM.LINE()} m2b={machine_EvonyClient_N.method_to_body}')
  m2bk_sorted = sorted(machine_EvonyClient_N.method_to_body.keys())
  nPerLine = 15
  nM2B = len(machine_EvonyClient_N.method_to_body)
  for ix1 in range(0, nM2B, nPerLine):
    print(f'[{ix1}]: ', end='')
    for ix2 in range(ix1, min(ix1 + nPerLine, nM2B), 1):
      key = m2bk_sorted[ix2]
      #print(f'\t[{key}]={machine_EvonyClient_N.method_to_body[key]},  ', end='')
      print(f'[{key}]={machine_EvonyClient_N.method_to_body[key]},  ', end='')
    print(f'')

  assert 1==2, 'TODO'

def test_TEV0000_EvC_SomeHints(raw_do_abc_tag_EvonyClient_N: Tag):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  print(f'# ## Parameters for machine_EvonyClient_N.call_method')
  print(f'# some info in: ActionScript Virtual Machine 2 Overview (108pp)')
  print(f'# 3.3.3 Method Entry: talks about three local data areas are allocated for it, as outlined in Chapter 2.')
  print(f'# >> 2.5.8 for calling class (static) methods, use callstatic')
  print(f'# ')

def test_TEV1000_EvC_execute_tag_EvonyClient_N(raw_do_abc_tag_EvonyClient_N: Tag):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  print(f'## @{BM.LINE()} type(raw_do_abc_tag_EvonyClient_N)={type(raw_do_abc_tag_EvonyClient_N)}')
  execute_tag(raw_do_abc_tag_EvonyClient_N)

def test_TEV1100_execute_do_abc_tag_EvonyClient_N(do_abc_tag_EvonyClient_N: DoABCTag):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  execute_do_abc_tag(do_abc_tag_EvonyClient_N)

def test_TEV1200_lookup_class_EvonyClient_N(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  ix = 0
  for item in machine_EvonyClient_N.name_to_class:
    if BM.IsSignificantBinary(ix): print(f'  ##{ix} n2c={item} > {machine_EvonyClient_N.lookup_class(item)}')
    ix += 1
  print(f'## @{BM.LINE()} $$ machine_EvonyClient_N={machine_EvonyClient_N}')
  assert len(machine_EvonyClient_N.name_to_class) == 87 # -111
  #assert machine_EvonyClient_N.lookup_class('com.evony.util.UIUtil') == 2241
  assert machine_EvonyClient_N.lookup_class('mx.core:IChildList') == 1
  assert machine_EvonyClient_N.lookup_class('_EvonyClient_mx_managers_SystemManager') == 6
  assert machine_EvonyClient_N.lookup_class('mx.managers:IFocusManagerContainer') == 8
  assert machine_EvonyClient_N.lookup_class('mx.core:RSLListLoader') == 66
  # assert len(machine_heroes.name_to_class) == 3739
  # assert machine_heroes.lookup_class('battle.BattleCore') == 2241
  # assert machine_heroes.lookup_class('game.battle.controller.BattleController') == 989
  # assert machine_heroes.lookup_class('game.battle.controller.BattleEnemyReward') == 2308

def test_TEV1300_lookup_method(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  ix = 0
  for item in machine_EvonyClient_N.name_to_method:
    if BM.IsSignificantBinary(ix): print(f'  ##{ix} n2m={item} > {machine_EvonyClient_N.lookup_method(item)}')
    ix += 1
  assert len(machine_EvonyClient_N.name_to_method) == 77 # -111
  assert machine_EvonyClient_N.lookup_method('mx.managers:SystemManager.getSWFRoot') == 127
  assert machine_EvonyClient_N.lookup_method('mx.utils:StringUtil.trimArrayElements') == 951
  # not found # assert machine_EvonyClient_N.lookup_method('view.ui.TimeLabel.getDateStr') == 9999
  # not found # assert machine_EvonyClient_N.lookup_method('com.evony.Context.getTimeDiff') == 9999
  assert machine_EvonyClient_N.lookup_method('mx.utils:StringUtil.trim') == 950 # Mainflash/mx/utils/StringUtil.as:18

def test_TEV1400_call_StringUtil_trim(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  print(f'## @{BM.LINE()} ## ../mx/utils/StringUtil.as')
  print(f'## @{BM.LINE()} package mx.utils{{ .. import mx.core.mx_internal .. use namespace mx_internal ')
  print(f'## @{BM.LINE()}  public class StringUtil {{')
  print(f'## @{BM.LINE()}   ...')
  print(f'## @{BM.LINE()}   public static function trim(param1:String) : String {{')
  print(f'## @{BM.LINE()}    if(param1 == null) {{ return ""; }}')
  print(f'## @{BM.LINE()}    var _loc2_:int = 0;')
  print(f'## @{BM.LINE()}    while(isWhitespace(param1.charAt(_loc2_))) {{ _loc2_++; }}')
  print(f'## @{BM.LINE()}    var _loc3_:int = param1.length - 1;')
  print(f'## @{BM.LINE()}    while(isWhitespace(param1.charAt(_loc3_))) {{ _loc3_--; }}')
  print(f'## @{BM.LINE()}    if(_loc3_ >= _loc2_) {{ return param1.slice(_loc2_,_loc3_ + 1); }}')
  print(f'## @{BM.LINE()}    return ""; }}')

  # EvonyHuge.txt:147605 # public static function trim(param1:String) : String
  callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100, loggingLevel = logging.DEBUG)
  machine_EvonyClient_N.cbOnInsExe = callback

  #machine_EvonyClient_N.abc_file.propagateStrings(BM.LINE(False)) # get class names etc propagated

  # do class init
  ixClass = 67
  assert machine_EvonyClient_N.abc_file.classes[ixClass].nam_name == 'mx.utils:StringUtil' # right class
  assert machine_EvonyClient_N.abc_file.classes[ixClass].init_ix == 949 # right class init method
  act = machine_EvonyClient_N.call_static(machine_EvonyClient_N.abc_file.classes[ixClass].init_ix, '')
  print(f'## @{BM.LINE()} SU_T init=<{act}>')

  # act = machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', "xyz", None) # eould return empty string, but asserts as charAt fails to be found
  # act = machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', undefined, "xyz") # that undefined throws an assertion PushScope
  # act = machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', None, "xyz") # PushScope asserts
  act = machine_EvonyClient_N.call_static('mx.utils:StringUtil.trim', '', "xyz")
  machine_EvonyClient_N.cbOnInsExe = None
  print(f'## @{BM.LINE()} SU_T act=<{act}>')
  assert machine_EvonyClient_N.call_static('mx.utils:StringUtil.trim', "xyz") == "xyz"
  assert machine_EvonyClient_N.call_static('mx.utils:StringUtil.trim', "  abc  ") == "abc"

@pytest.mark.skip(reason="change to fit Evony") # import pytest
def test_TEV1500_call_hitrate_intensity(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  # scripts/battle/BattleCore.as:57 public static function hitrateIntensity(param1:int, param2:int, param3:int = 4) : Number
  assert machine_EvonyClient_N.call_method('battle:BattleCore.hitrateIntensity', undefined, -100, 0) == 1
  assert machine_EvonyClient_N.call_method('battle:BattleCore.hitrateIntensity', undefined, 100, 0) == 1
  assert machine_EvonyClient_N.call_method('battle:BattleCore.hitrateIntensity', undefined, 0, 100) == 0
  assert machine_EvonyClient_N.call_method('battle:BattleCore.hitrateIntensity', undefined, 4, 8) == 0.5

@pytest.mark.skip(reason="change to fit Evony") # import pytest
def test_TEV1600_new_battle_enemy_reward(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  machine_EvonyClient_N.new_instance('game.battle.controller:BattleEnemyReward')
