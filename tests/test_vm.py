from avm2.runtime import undefined
from avm2.swf.swf_types import DoABCTag, Tag
from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
from avm2.abc.abc_instructions import CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace
import inspect, sys
import os

# ln -s ~/git/BDL/Games/Evony/PythonBits/MyGamesHelper.py (in git/python-avm2_AdobeSwfActionScript)
# ln -s ~/git/BDL/Games/Evony/PythonBits/BrewMaths.py (in git/python-avm2_AdobeSwfActionScript)
##!! import MyGamesHelper as MGH
import BrewMaths as BM

#from /home/bryan/git/BDL/Games/Evony/PythonBits/MyGamesHelper import MyGamesHelper as MGH

# run via 'pytest -s' (that's pytest-3), to get 'being run ##' messages

def test_THV1000_execute_tag_heroes(raw_do_abc_tag_heroes: Tag):
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    print(f'## type(raw_do_abc_tag_heroes)={type(raw_do_abc_tag_heroes)}')
    execute_tag(raw_do_abc_tag_heroes)

def test_THV1100_execute_do_abc_tag_heroes(do_abc_tag_heroes: DoABCTag):
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    execute_do_abc_tag(do_abc_tag_heroes)

def test_THV1200_lookup_class_heroes(machine_heroes: VirtualMachine):
    ##!! MGH.PrintTestBeingRun(0)
    print(f'## os.getcwd()={os.getcwd()}')
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    ix = 0
    for item in machine_heroes.name_to_class:
      if BM.IsSignificantBinary(ix): print(f'  ##{ix} n2c={item} > {machine_heroes.lookup_class(item)}')
      ix += 1
    assert len(machine_heroes.name_to_class) == 3739
    assert machine_heroes.lookup_class('battle:BattleCore') == 2241 # scripts/battle/BattleCore.as
    assert machine_heroes.lookup_class('game.battle.controller:BattleController') == 989 # scripts/game/battle/controller/BattleController.as
    assert machine_heroes.lookup_class('game.battle.controller:BattleEnemyReward') == 2308 # scripts/game/battle/controller/BattleEnemyReward.as
    assert machine_heroes.lookup_class('game.data.storage.loot:LootBoxDropItemDescription') == 2048 # scripts/game/data/storage/loot/LootBoxDropItemDescription.as

def test_THV1300_lookup_method_heroes(machine_heroes: VirtualMachine):
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    ix = 0
    for item in machine_heroes.name_to_method:
      if BM.IsSignificantBinary(ix): print(f'  ##{ix} n2m={item} > {machine_heroes.lookup_method(item)}')
      ix += 1
    assert len(machine_heroes.name_to_method) == 1074
    assert machine_heroes.lookup_method('battle:BattleCore.getElementalPenetration') == 24363 # scripts/battle/BattleCore.as:85
    assert machine_heroes.lookup_method('battle:BattleCore.hitrateIntensity') == 24360 # scripts/battle/BattleCore.as:57
    assert machine_heroes.lookup_method('game.mediator.gui.popup.hero:UnitUtils.createDescription') == 12801 # scripts/game/mediator/gui/popup/hero/UnitUtils.as:24

def test_THV1400_call_get_elemental_penetration_heroes(machine_heroes: VirtualMachine):
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    # scripts/battle/BattleCore.as:85 public static function getElementalPenetration(param1:Number, param2:Number) : int
    callback = CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(100)
    machine_heroes.cbOnInsExe = callback
    assert machine_heroes.call_method('battle:BattleCore.getElementalPenetration', undefined, 2, 300000) == 1
    print(f'## @{BM.LINE()} mark ##')
    assert machine_heroes.call_method('battle:BattleCore.getElementalPenetration', undefined, 42, -100500) == 42

def test_THV1500_call_hitrate_intensity_heroes(machine_heroes: VirtualMachine):
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    # scripts/battle/BattleCore.as:57 public static function hitrateIntensity(param1:int, param2:int, param3:int = 4) : Number
    assert machine_heroes.call_method('battle:BattleCore.hitrateIntensity', undefined, -100, 0) == 1
    assert machine_heroes.call_method('battle:BattleCore.hitrateIntensity', undefined, 100, 0) == 1
    assert machine_heroes.call_method('battle:BattleCore.hitrateIntensity', undefined, 0, 100) == 0
    assert machine_heroes.call_method('battle:BattleCore.hitrateIntensity', undefined, 4, 8) == 0.5

def test_THV1600_new_battle_enemy_reward_heroes(machine_heroes: VirtualMachine):
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    machine_heroes.new_instance('game.battle.controller:BattleEnemyReward')
