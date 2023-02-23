from avm2.runtime import undefined
from avm2.swf.types import DoABCTag, Tag
from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
import inspect, sys
import MyGamesHelper as MGH # ln -s ~/git/BDL/Games/Evony/PythonBits/MyGamesHelper.py (in git/python-avm2_AdobeSwfActionScript)
#from /home/bryan/git/BDL/Games/Evony/PythonBits/MyGamesHelper import MyGamesHelper as MGH

# run via 'pytest -s' (that's pytest-3), to get 'being run ##' messages

def test_T1000_execute_tag_heroes(raw_do_abc_tag_heroes: Tag):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    execute_tag(raw_do_abc_tag_heroes)

def test_T1100_execute_do_abc_tag_heroes(do_abc_tag_heroes: DoABCTag):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    execute_do_abc_tag(do_abc_tag_heroes)

def test_T1200_lookup_class(machine_heroes: VirtualMachine):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    ix = 0
    for nm in machine_heroes.name_to_class:
      if IsSignificantBinary(ix): print(f' ## n@c={nm}')
      ++ix
    assert machine_heroes.lookup_class('battle.BattleCore') == 2241
    assert machine_heroes.lookup_class('game.battle.controller.BattleController') == 989
    assert machine_heroes.lookup_class('game.battle.controller.BattleEnemyReward') == 2308

def test_T1300_lookup_method(machine_heroes: VirtualMachine):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    assert machine_heroes.lookup_method('battle.BattleCore.getElementalPenetration') == 24363
    assert machine_heroes.lookup_method('battle.BattleCore.hitrateIntensity') == 24360

def test_T1400_call_get_elemental_penetration(machine_heroes: VirtualMachine):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    assert machine_heroes.call_method('battle.BattleCore.getElementalPenetration', undefined, 2, 300000) == 1
    assert machine_heroes.call_method('battle.BattleCore.getElementalPenetration', undefined, 42, -100500) == 42

def test_T1500_call_hitrate_intensity(machine_heroes: VirtualMachine):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    assert machine_heroes.call_method('battle.BattleCore.hitrateIntensity', undefined, -100, 0) == 1
    assert machine_heroes.call_method('battle.BattleCore.hitrateIntensity', undefined, 100, 0) == 1
    assert machine_heroes.call_method('battle.BattleCore.hitrateIntensity', undefined, 0, 100) == 0
    assert machine_heroes.call_method('battle.BattleCore.hitrateIntensity', undefined, 4, 8) == 0.5

def test_T1600_new_battle_enemy_reward(machine_heroes: VirtualMachine):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    machine_heroes.new_instance('game.battle.controller.BattleEnemyReward')
