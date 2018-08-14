from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
from avm2.swf.types import DoABCTag, Tag
from avm2.abc.types import ABCMethodIndex


def test_execute_tag(raw_do_abc_tag: Tag):
    execute_tag(raw_do_abc_tag)


def test_execute_do_abc_tag(do_abc_tag: DoABCTag):
    execute_do_abc_tag(do_abc_tag)


def test_lookup_class(machine: VirtualMachine):
    assert machine.lookup_class('battle.BattleCore') == 2241
    assert machine.lookup_class('game.battle.controller.BattleController') == 989


def test_lookup_method(
    get_elemental_penetration_method_index: ABCMethodIndex,
    hitrate_intensity_method_index: ABCMethodIndex,
):
    assert get_elemental_penetration_method_index == 24363
    assert hitrate_intensity_method_index == 24360


def test_execute_get_elemental_penetration(machine: VirtualMachine, get_elemental_penetration_method_index: ABCMethodIndex):
    assert machine.execute_method(get_elemental_penetration_method_index, ..., 2, 300000) == 1
    assert machine.execute_method(get_elemental_penetration_method_index, ..., 42, -100500) == 42


def test_execute_hitrate_intensity(machine: VirtualMachine, hitrate_intensity_method_index: ABCMethodIndex):
    assert machine.execute_method(hitrate_intensity_method_index, ..., -100, 0) == 1
    assert machine.execute_method(hitrate_intensity_method_index, ..., 100, 0) == 1
    assert machine.execute_method(hitrate_intensity_method_index, ..., 0, 100) == 0
    assert machine.execute_method(hitrate_intensity_method_index, ..., 4, 8) == 0.5
