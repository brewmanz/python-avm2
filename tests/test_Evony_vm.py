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

def test_E_T0000_EvC_SomeHints(raw_do_abc_tag_EvonyClient_N: Tag):
    print(f'## @{BM.LINE()} being run ##')
    print(f'# ## Parameters for machine_EvonyClient_N.call_method')
    print(f'# some info in: ActionScript Virtual Machine 2 Overview (108pp)')
    print(f'# 3.3.3 Method Entry: talks about three local data areas are allocated for it, as outlined in Chapter 2.')
    print(f'# >> 2.5.8 for calling class (static) methods, use callstatic')
    print(f'# ')

def test_E_T1000_EvC_execute_tag_EvonyClient_N(raw_do_abc_tag_EvonyClient_N: Tag):
    print(f'## @{BM.LINE()} being run ##')
    print(f'## @{BM.LINE()} type(raw_do_abc_tag_EvonyClient_N)={type(raw_do_abc_tag_EvonyClient_N)}')
    execute_tag(raw_do_abc_tag_EvonyClient_N)

def test_E_T1100_execute_do_abc_tag_EvonyClient_N(do_abc_tag_EvonyClient_N: DoABCTag):
    print(f'## @{BM.LINE()} being run ##')
    execute_do_abc_tag(do_abc_tag_EvonyClient_N)

def test_E_T1200_lookup_class_EvonyClient_N(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
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

def test_E_T1300_lookup_method(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
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

def test_E_T1400_call_StringUtil_trim(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
    # EvonyHuge.txt:147605 # public static function trim(param1:String) : String
    callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100)
    machine_EvonyClient_N.callbackOnInstructionExecuting = callback
    act = machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', "xyz")
    machine_EvonyClient_N.callbackOnInstructionExecuting = None
    print(f'## @{BM.LINE()} SU_T act=<{act}>')
    assert machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', "xyz") == "xyz"
    assert machine_EvonyClient_N.call_static('mx.utils.StringUtil.trim', "  abc  ") == "abc"

@pytest.mark.skip(reason="change to fit Evony") # import pytest
def test_E_T1500_call_hitrate_intensity(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
    # scripts/battle/BattleCore.as:57 public static function hitrateIntensity(param1:int, param2:int, param3:int = 4) : Number
    assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, -100, 0) == 1
    assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 100, 0) == 1
    assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 0, 100) == 0
    assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 4, 8) == 0.5

@pytest.mark.skip(reason="change to fit Evony") # import pytest
def test_E_T1600_new_battle_enemy_reward(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
    machine_EvonyClient_N.new_instance('game.battle.controller.BattleEnemyReward')
