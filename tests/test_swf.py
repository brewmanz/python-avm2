from __future__ import annotations

from avm2.swf.parser import parse_swf
from avm2.swf.types import DoABCTag, DoABCTagFlags

import inspect

def test_parse_swf_1_HexChunk(swf_1_HexChunk: memoryview):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    assert len(list(parse_swf(swf_1_HexChunk))) == 5


def test_parse_swf_2_heroes(swf_2_heroes: memoryview):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    assert len(list(parse_swf(swf_2_heroes))) == 10


def test_parse_swf_3_Farm(swf_3_Farm: memoryview):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    assert len(list(parse_swf(swf_3_Farm))) == 1995


def test_parse_swf_4_EpicGame(swf_4_EpicGame: memoryview):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    assert len(list(parse_swf(swf_4_EpicGame))) == 9


def test_do_abc_tag_2_heroes(do_abc_tag_heroes: DoABCTag):
    print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    assert do_abc_tag_heroes.flags == DoABCTagFlags.LAZY_INITIALIZE
    assert do_abc_tag_heroes.name == 'merged'
    assert do_abc_tag_heroes.abc_file
