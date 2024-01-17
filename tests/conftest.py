from pathlib import Path

from pytest import fixture

import inspect
import tests
from avm2.abc.abc_types import ABCFile
from avm2.io import MemoryViewReader
from avm2.swf.swf_enums import TagType
from avm2.swf.swf_parser import parse_swf
from avm2.swf.swf_types import DoABCTag, Tag
from avm2.vm import VirtualMachine

# run via 'pytest -s' (that's pytest-3), to get 'being run ##' messages. in ~/git/python-avm2_AdobeSwfActionScript

import MyGamesHelper as MGH
import BrewMaths as BM
import os
base_path = Path(tests.__file__).parent.parent / 'data'

@fixture(scope='session')
# def swf_EvonyClient_N(ver: str) -> bytes: # somehow maybe do it like this, but so it works!
def swf_EvonyClient_N() -> bytes:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    # if ver == '1922':
    return (base_path / 'EvonyClient1922.swf').read_bytes()

@fixture(scope='session')
def raw_do_abc_tag_EvonyClient_N(swf_EvonyClient_N: memoryview) -> Tag: # , N: int) -> Tag:
    ##!! MGH.PrintTestBeingRun(0)
    print(f'## os.getcwd()={os.getcwd()}\n')
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    count = 0
    for tag in parse_swf(swf_EvonyClient_N):
        if tag.type_ == TagType.DO_ABC:
            ++count
            #if count == N:
              # return tag
            return tag

@fixture(scope='session')
def do_abc_tag_EvonyClient_N(raw_do_abc_tag_EvonyClient_N: Tag) -> DoABCTag: # , N: int) -> DoABCTag:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return DoABCTag(raw_do_abc_tag_EvonyClient_N.raw)


@fixture(scope='session')
def abc_file_EvonyClient_N(do_abc_tag_EvonyClient_N: DoABCTag) -> ABCFile: # , N: int
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return ABCFile(MemoryViewReader(do_abc_tag_EvonyClient_N.abc_file))


@fixture(scope='session')
def machine_EvonyClient_N(abc_file_EvonyClient_N: ABCFile) -> VirtualMachine: # , N: int) -> VirtualMachine:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return VirtualMachine(abc_file_EvonyClient_N)

####

@fixture(scope='session')
def swf_1_HexChunk() -> bytes:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return bytes.fromhex(
        '465753034F0000007800055F00000FA000000C01004302FFFFFFBF0023000000'
        '010070FB49970D0C7D50000114000000000125C9920D21ED488765303B6DE1D8'
        'B40000860606010001000040000000'
    )


@fixture(scope='session')
def swf_2_heroes() -> bytes:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return (base_path / 'heroes.swf').read_bytes()


@fixture(scope='session')
def swf_3_Farm() -> bytes:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return (base_path / 'Farm_d_13_9_2_2198334.swf').read_bytes()


@fixture(scope='session')
def swf_4_EpicGame() -> bytes:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return (base_path / 'EpicGame.swf').read_bytes()


@fixture(scope='session')
def raw_do_abc_tag_heroes(swf_2_heroes: memoryview) -> Tag:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    for tag in parse_swf(swf_2_heroes):
        if tag.type_ == TagType.DO_ABC:
            return tag


@fixture(scope='session')
def do_abc_tag_heroes(raw_do_abc_tag_heroes: Tag) -> DoABCTag:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return DoABCTag(raw_do_abc_tag_heroes.raw)


@fixture(scope='session')
def abc_file_heroes(do_abc_tag_heroes: DoABCTag) -> ABCFile:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return ABCFile(MemoryViewReader(do_abc_tag_heroes.abc_file))


@fixture(scope='session')
def machine_heroes(abc_file_heroes: ABCFile) -> VirtualMachine:
    print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')
    return VirtualMachine(abc_file_heroes)

if __name__ == '__main__':  # when you run 'python thisModuleName.py' ...
  import doctest, os, sys
  print(f'@{BM.LINE()} ### run embedded unit tests via \'python ' + os.path.basename(__file__) + '\'')
  res = doctest.testmod() # then the tests in block comments will run
  print(f'@{BM.LINE()} ### BTW res = <{res}>, res.failed=<{res.failed}>')
  sys.exit(res.failed) # return number of failed tests
