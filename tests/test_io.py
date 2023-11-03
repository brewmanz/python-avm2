import pytest
import inspect

import BrewMaths as BM

from avm2.io import MemoryViewReader

def test_T1100_memory_view_reader_read():
    #print(f'## {inspect.currentframe().f_code.co_filename}:{inspect.currentframe().f_code.co_firstlineno}({inspect.currentframe().f_code.co_name}) being run ##')
    print(f'## @{BM.LINE()} being run ##')
    reader = MemoryViewReader(b'abc')
    assert reader.read(1) == b'a'
    assert reader.read(2) == b'bc'
    assert reader.read(1) == b''


def test_T1200_memory_view_reader_skip():
    print(f'## @{BM.LINE()} being run ##')
    assert MemoryViewReader(b'abc').skip(1) == 1


def test_T2000_memory_view_reader_read_all():
    print(f'## @{BM.LINE()} being run ##')
    reader = MemoryViewReader(b'abc')
    reader.skip(1)
    assert reader.read_all() == b'bc'
    assert reader.read_all() == b''


def test_T2100_memory_view_reader_read_u8():
    print(f'## @{BM.LINE()} being run ##')
    assert MemoryViewReader(b'\x0A').read_u8() == 0x0A


def test_T2200_memory_view_reader_read_u16():
    print(f'## @{BM.LINE()} being run ##')
    assert MemoryViewReader(b'WS').read_u16() == 0x5357


def test_T2300_memory_view_reader_read_u32():
    print(f'## @{BM.LINE()} being run ##')
    assert MemoryViewReader(b'\x0D\x0C\x0B\x0A').read_u32() == 0x0A0B0C0D


@pytest.mark.parametrize('bytes_, expected', [
    (b'\x0C\x0B\x0A', 0x0A0B0C),
    (b'\xFF\xFF\xFF', -1),
])
def test_T2400_memory_view_reader_read_s24(bytes_: bytes, expected: int):
    print(f'## @{BM.LINE()} being run ##')
    assert MemoryViewReader(bytes_).read_s24() == expected


def test_T2500_memory_view_reader_read_until():
    print(f'## @{BM.LINE()} being run ##')
    reader = MemoryViewReader(b'ABCDE')
    reader.skip(1)
    assert reader.read_until(ord('D')) == b'BC'
    assert reader.position == 4


def test_T2600_memory_view_reader_read_string():
    print(f'## @{BM.LINE()} being run ##')
    assert MemoryViewReader(b'AB\x00CD').read_string() == 'AB'


@pytest.mark.parametrize('bytes_, unsigned, value', [
    (b'\x7F', True, 0x7F),
    (b'\xFF\x7F', True, 0x3FFF),
    (b'\xFF\xFF\x7F', True, 0x1FFFFF),
    (b'\xFF\xFF\xFF\x7F', True, 0xFFFFFFF),
    (b'\xFF\xFF\xFF\xFF\x0F', True, 0xFFFFFFFF),
    (b'\xFF\xFF\xFF\xFF\x7F', False, -1),
    (b'\x7F', False, -1),
    (b'\x0F', False, 15),
])
def test_T2700_memory_view_reader_read_int(bytes_: bytes, unsigned: bool, value: int):
    print(f'## @{BM.LINE()} being run ##')
    assert MemoryViewReader(bytes_).read_int(unsigned) == value


def test_is_eof():
    print(f'## @{BM.LINE()} being run ##')
    reader = MemoryViewReader(b'ABCDE')
    assert not reader.is_eof()
    reader.read(4)
    assert not reader.is_eof()
    reader.read(2)
    assert reader.is_eof()
    reader.skip(42)
    assert reader.is_eof()
