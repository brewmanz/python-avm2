from avm2.runtime import undefined
from avm2.swf.types import DoABCTag, Tag
from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
import inspect, sys

# ln -s ~/git/BDL/Games/Evony/PythonBits/MyGamesHelper.py (in git/python-avm2_AdobeSwfActionScript)
# ln -s ~/git/BDL/Games/Evony/PythonBits/BrewMaths.py (in git/python-avm2_AdobeSwfActionScript)
import MyGamesHelper as MGH
import BrewMaths as BM

#from /home/bryan/git/BDL/Games/Evony/PythonBits/MyGamesHelper import MyGamesHelper as MGH

# run via 'pytest -s' (that's pytest-3), to get 'being run ##' messages

def test_T1000_EvC_execute_tag_EvonyClient_N(raw_do_abc_tag_EvonyClient_N: Tag):
    print(f'## @{BM.LINE()} being run ##')
    print(f'## @{BM.LINE()} type(raw_do_abc_tag_EvonyClient_N)={type(raw_do_abc_tag_EvonyClient_N)}')
    execute_tag(raw_do_abc_tag_EvonyClient_N)

def test_T1100_execute_do_abc_tag_EvonyClient_N(do_abc_tag_EvonyClient_N: DoABCTag):
    print(f'## @{BM.LINE()} being run ##')
    execute_do_abc_tag(do_abc_tag_EvonyClient_N)

def test_T1200_lookup_class_EvonyClient_N(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
    ix = 0
    for item in machine_EvonyClient_N.name_to_class:
      if BM.IsSignificantBinary(ix): print(f'  ##{ix} n2c={item} > {machine_EvonyClient_N.lookup_class(item)}')
      ix += 1
    assert len(machine_EvonyClient_N.machine_heroes.name_to_class) == -111
    assert machine_EvonyClient_N.lookup_class('com.evony.util.UIUtil') == 2241
    assert machine_EvonyClient_N.lookup_class('game.battle.controller.BattleController') == 989
    assert machine_EvonyClient_N.lookup_class('game.battle.controller.BattleEnemyReward') == 2308
    # assert machine_EvonyClient_N.lookup_class('battle.BattleCore') == 2241
    # assert machine_EvonyClient_N.lookup_class('game.battle.controller.BattleController') == 989
    # assert machine_EvonyClient_N.lookup_class('game.battle.controller.BattleEnemyReward') == 2308

def test_T1300_lookup_method(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
    ix = 0
    for item in machine_EvonyClient_N.name_to_method:
      if BM.IsSignificantBinary(ix): print(f'  ##{ix} n2m={item} > {machine_EvonyClient_N.lookup_method(item)}')
      ix += 1
    assert len(machine_EvonyClient_N.name_to_method) == -111
    assert machine_EvonyClient_N.lookup_method('battle.BattleCore.getElementalPenetration') == 24363
    assert machine_EvonyClient_N.lookup_method('battle.BattleCore.hitrateIntensity') == 24360

def test_T1400_call_get_elemental_penetration_EvonyClient_N(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
    assert machine_EvonyClient_N.call_method('battle.BattleCore.getElementalPenetration', undefined, 2, 300000) == 1
    assert machine_EvonyClient_N.call_method('battle.BattleCore.getElementalPenetration', undefined, 42, -100500) == 42

def test_T1500_call_hitrate_intensity(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
    assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, -100, 0) == 1
    assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 100, 0) == 1
    assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 0, 100) == 0
    assert machine_EvonyClient_N.call_method('battle.BattleCore.hitrateIntensity', undefined, 4, 8) == 0.5

def test_T1600_new_battle_enemy_reward(machine_EvonyClient_N: VirtualMachine):
    print(f'## @{BM.LINE()} being run ##')
    machine_EvonyClient_N.new_instance('game.battle.controller.BattleEnemyReward')
