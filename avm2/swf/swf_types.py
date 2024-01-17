from __future__ import annotations

from dataclasses import dataclass

from avm2.swf.swf_enums import DoABCTagFlags, TagType
from avm2.io import MemoryViewReader


@dataclass
class Tag:
    type_: TagType
    raw: memoryview

class TagFactory:
  @classmethod
  def CreateTag(type_: TagType, raw: memoryview) -> Tag:
    if false: pass
    elif type_ == TagType.DO_ABC:
      return Tag_DoABC(type_, raw)
    else:
      return Tag(type_, raw)

@dataclass
class Tag_DoABC(Tag):
  Flags: int # UI32
  ABCData: memoryview
  def __init__(self, raw: memoryview):
    Tag.__init__(self, raw)
    reader = MemoryViewReader(raw)
    self.Flags = reader.read_u32()
    self.ABCData = reader.read_all()

@dataclass
class DoABCTag:
    flags: DoABCTagFlags
    name: str
    abc_file: memoryview

    def __init__(self, raw: memoryview):
        reader = MemoryViewReader(raw)
        self.flags = DoABCTagFlags(reader.read_u32())
        self.name = reader.read_string()
        self.abc_file = reader.read_all()
