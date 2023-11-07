from __future__ import annotations

import BrewMaths as BM

from avm2.swf.parser import parse_swf
from avm2.swf.types import DoABCTag, DoABCTagFlags

def test_parse_swf_EvonyClient_N(swf_EvonyClient_N: memoryview):
    print(f'## @{BM.LINE()} being run ##')
    assert len(swf_EvonyClient_N) == 4318377
    assert len(list(parse_swf(swf_EvonyClient_N))) == 1114

def test_parse_swf_1_HexChunk(swf_1_HexChunk: memoryview):
    print(f'## @{BM.LINE()} being run ##')
    assert len(swf_1_HexChunk) == 79
    assert len(list(parse_swf(swf_1_HexChunk))) == 5

def test_parse_swf_2_heroes(swf_2_heroes: memoryview):
    print(f'## @{BM.LINE()} being run ##')
    assert len(swf_2_heroes) == 1383092
    assert len(list(parse_swf(swf_2_heroes))) == 10

def test_parse_swf_3_Farm(swf_3_Farm: memoryview):
    print(f'## @{BM.LINE()} being run ##')
    assert len(swf_3_Farm) == 2799105
    assert len(list(parse_swf(swf_3_Farm))) == 1995

def test_parse_swf_4_EpicGame(swf_4_EpicGame: memoryview):
    print(f'## @{BM.LINE()} being run ##')
    assert len(swf_4_EpicGame) == 1460606
    assert len(list(parse_swf(swf_4_EpicGame))) == 9

def test_do_abc_tag_2_heroes(do_abc_tag_heroes: DoABCTag):
    print(f'## @{BM.LINE()} being run ##')
    assert do_abc_tag_heroes.flags == DoABCTagFlags.LAZY_INITIALIZE
    assert do_abc_tag_heroes.name == 'merged'
    assert do_abc_tag_heroes.abc_file
