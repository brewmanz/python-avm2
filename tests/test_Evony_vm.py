from avm2.runtime import undefined
from avm2.swf.types import DoABCTag, Tag
from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
from avm2.abc.instructions import CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace
import inspect, sys
import pytest

# to run selected tests # pytest -k "test_E_T1400 or test_T1400" -s
# ln -s ~/git/BDL/Games/Evony/PythonBits/MyGamesHelper.py (in git/python-avm2_AdobeSwfActionScript)
# ln -s ~/git/BDL/Games/Evony/PythonBits/BrewMaths.py (in git/python-avm2_AdobeSwfActionScript)
import MyGamesHelper as MGH
import BrewMaths as BM

#from /home/bryan/git/BDL/Games/Evony/PythonBits/MyGamesHelper import MyGamesHelper as MGH

# run via 'pytest -s' (that's pytest-3), to get 'being run ##' messages

def test_TEV4000_EvC_HospitalWin_bits(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  assert 1 == 2

def test_TEV3000_EvC_toDebugString_VariousBeans(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  assert 1 == 2

def test_TEV2120_InitAllClasseInstances(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  # empty # for item in machine_EvonyClient_N.class_objects:
  print(f'@{BM.LINE()} class count = {len(machine_EvonyClient_N.abc_file.classes)}')
  assert len(machine_EvonyClient_N.abc_file.classes) == len(machine_EvonyClient_N.abc_file.instances), 'Sanity check'
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
      act = machine_EvonyClient_N.call_static(itemI.init_ix, '')
      print(f'## @{BM.LINE()} init res=<{act}>')

def test_TEV2110_InitAllClasses(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  # empty # for item in machine_EvonyClient_N.class_objects:
  print(f'@{BM.LINE()} class count = {len(machine_EvonyClient_N.abc_file.classes)}')
  assert len(machine_EvonyClient_N.abc_file.classes) == len(machine_EvonyClient_N.abc_file.instances), 'Sanity check'
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
      act = machine_EvonyClient_N.call_static(itemC.init_ix, '')
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
  assert machine_EvonyClient_N.lookup_class('mx.core.IChildList') == 1
  assert machine_EvonyClient_N.lookup_class('_EvonyClient_mx_managers_SystemManager') == 6
  assert machine_EvonyClient_N.lookup_class('mx.managers.IFocusManagerContainer') == 8
  assert machine_EvonyClient_N.lookup_class('mx.core.RSLListLoader') == 66
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
  assert machine_EvonyClient_N.lookup_method('mx.managers.SystemManager.getSWFRoot') == 127
  assert machine_EvonyClient_N.lookup_method('mx.utils.StringUtil.trimArrayElements') == 951
  # not found # assert machine_EvonyClient_N.lookup_method('view.ui.TimeLabel.getDateStr') == 9999
  # not found # assert machine_EvonyClient_N.lookup_method('com.evony.Context.getTimeDiff') == 9999
  assert machine_EvonyClient_N.lookup_method('mx.utils.StringUtil.trim') == 950 # Mainflash/mx/utils/StringUtil.as:18

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
  callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100)
  machine_EvonyClient_N.cbOnInsExe = callback

  #machine_EvonyClient_N.abc_file.propagateStrings(BM.LINE(False)) # get class names etc propagated

  # do class init
  ixClass = 67
  assert machine_EvonyClient_N.abc_file.classes[ixClass].nam_name == 'mx.utils.StringUtil' # right class
  assert machine_EvonyClient_N.abc_file.classes[ixClass].init_ix == 949 # right class init method
  act = machine_EvonyClient_N.call_static(machine_EvonyClient_N.abc_file.classes[ixClass].init_ix, '')
  print(f'## @{BM.LINE()} SU_T init=<{act}>')

  # act = machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', "xyz", None) # eould return empty string, but asserts as charAt fails to be found
  # act = machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', undefined, "xyz") # that undefined throws an assertion PushScope
  # act = machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', None, "xyz") # PushScope asserts
  act = machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', '', "xyz")
  machine_EvonyClient_N.cbOnInsExe = None
  print(f'## @{BM.LINE()} SU_T act=<{act}>')
  assert machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', "xyz") == "xyz"
  assert machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', "  abc  ") == "abc"

@pytest.mark.skip(reason="change to fit Evony") # import pytest
def test_TEV1500_call_hitrate_intensity(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  # scripts/battle/BattleCore.as:57 public static function hitrateIntensity(param1:int, param2:int, param3:int = 4) : Number
  assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, -100, 0) == 1
  assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 100, 0) == 1
  assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 0, 100) == 0
  assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 4, 8) == 0.5

@pytest.mark.skip(reason="change to fit Evony") # import pytest
def test_TEV1600_new_battle_enemy_reward(machine_EvonyClient_N: VirtualMachine):
  print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
  machine_EvonyClient_N.new_instance('game.battle.controller.BattleEnemyReward')
