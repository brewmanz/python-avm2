from __future__ import annotations

import BrewMaths as BM

from dataclasses import dataclass
from functools import partial
from typing import Optional, List, Union, NewType

from colorama import Fore, Style

import math
import BrewMaths as BM

from avm2.abc.enums import (
    ClassFlags,
    ConstantKind,
    MethodFlags,
    MultinameKind,
    NamespaceKind,
    TraitAttributes,
    TraitKind,
)
from avm2.abc.parser import read_array, read_array_with_default, read_string
from avm2.io import MemoryViewReader

ABCStringIndex = NewType('ABCStringIndex', int)
ABCNamespaceIndex = NewType('ABCNamespaceIndex', int)
ABCNamespaceSetIndex = NewType('ABCNamespaceSetIndex', int)
ABCMultinameIndex = NewType('ABCMultinameIndex', int)
ABCMethodIndex = NewType('ABCMethodIndex', int)
ABCMethodBodyIndex = NewType('ABCMethodBodyIndex', int)
ABCMetadataIndex = NewType('ABCMetadataIndex', int)
ABCClassIndex = NewType('ABCClassIndex', int)
ABCScriptIndex = NewType('ABCScriptIndex', int)


@dataclass
class ABCFile:
    minor_version: int
    major_version: int
    constant_pool: ASConstantPool
    methods: List[ASMethod]
    metadata: List[ASMetadata]
    instances: List[ASInstance]
    classes: List[ASClass]
    scripts: List[ASScript]
    method_bodies: List[ASMethodBody]

    def __init__(self, reader: MemoryViewReader):
        self.minor_version = reader.read_u16()
        self.major_version = reader.read_u16()
        self.constant_pool = ASConstantPool(reader)
        self.methods = read_array(reader, ASMethod)
        self.metadata = read_array(reader, ASMetadata)
        class_count = reader.read_int()
        self.instances = read_array(reader, ASInstance, class_count)
        self.classes = read_array(reader, ASClass, class_count)
        self.scripts = read_array(reader, ASScript)
        self.method_bodies = read_array(reader, ASMethodBody)


@dataclass
class ASConstantPool:
    integers: List[int]
    unsigned_integers: List[int]
    doubles: List[float]
    strings: List[str]
    namespaces: List[ASNamespace]
    ns_sets: List[ASNamespaceSet]
    multinames: List[ASMultiname]

    def __init__(self, reader: MemoryViewReader):
        self.integers = read_array_with_default(reader, partial(MemoryViewReader.read_int, unsigned=False), 0)
        self.unsigned_integers = read_array_with_default(reader, MemoryViewReader.read_int, 0)
        self.doubles = read_array_with_default(reader, MemoryViewReader.read_d64, math.nan)
        self.strings = read_array_with_default(reader, read_string, None)
        self.namespaces = read_array_with_default(reader, ASNamespace, None)
        self.ns_sets = read_array_with_default(reader, ASNamespaceSet, None)
        self.multinames = read_array_with_default(reader, ASMultiname, None)

    def propogateStrings(self):
      print(f'@{BM.LINE()} propogateStrings running ... ')
      print(f'@{BM.LINE()}  type(namespaces[-1])={type(self.namespaces[-1])}')
      for ix in range(len(self.namespaces)):
        item = self.namespaces[ix]
        if item != None:
          newItem = ASNamespaceBis(item, self.strings, ix)
          self.namespaces[ix] = newItem
      print(f'@{BM.LINE()}  type(namespaces[-1])={type(self.namespaces[-1])}')
      print(f'@{BM.LINE()}  type(ns_sets[-1])={type(self.ns_sets[-1])}')
      for ix in range(len(self.ns_sets)):
        item = self.ns_sets[ix]
        if item != None:
          newItem = ASNamespaceSetBis(item, self.namespaces, ix)
          self.ns_sets[ix] = newItem
      print(f'@{BM.LINE()}  type(ns_sets[-1])={type(self.ns_sets[-1])}')
      print(f'@{BM.LINE()}  type(multinames[-1])={type(self.multinames[-1])}')
      for ix in range(len(self.multinames)):
        item = self.multinames[ix]
        if item != None:
          newItem = ASMultinameBis(item, self.strings, self.namespaces, self.ns_sets, ix)
          self.multinames[ix] = newItem
      print(f'@{BM.LINE()}  type(multinames[-1])={type(self.multinames[-1])}')

@dataclass
class ASNamespace:
    kind: NamespaceKind
    nam_ix: ABCStringIndex

    def __init__(self, reader: MemoryViewReader):
        self.kind = NamespaceKind(reader.read_u8())
        self.nam_ix = reader.read_int()
@dataclass
class ASNamespaceBis(ASNamespace):
    ixCP: int
    nam_name: str

    def __init__(self, rhs: ASNamespace, listStrings: List[str], ixCP: int):
        self.kind = rhs.kind
        self.nam_ix = rhs.nam_ix
        self.ixCP = ixCP
        if rhs.nam_ix > 0 and rhs.nam_ix < len(listStrings):
          self.nam_name = listStrings[rhs.nam_ix]
        else:
          self.nam_name = None


@dataclass
class ASNamespaceSet:
    namespaces: List[ABCNamespaceIndex]

    def __init__(self, reader: MemoryViewReader):
        self.namespaces = read_array(reader, MemoryViewReader.read_int)
@dataclass
class ASNamespaceSetBis(ASNamespaceSet):
    ixCP: int
    ns_names: List[str]

    def __init__(self, rhs: ASNamespaceSet, listNamespaces: List[ASNamespaceBis], ixCP: int):
        self.namespaces = rhs.namespaces
        self.ixCP = ixCP
        names = list()
        for ix in range(len(self.namespaces)):
          ixNS = self.namespaces[ix]
          ns = listNamespaces[ixNS]
          nextName = ns.nam_name if ns else None
          # print(f'@{BM.LINE()}  nextName={nextName} ix={ix} ixNS={ixNS} ns={ns} rhs={rhs}')
          if True or nextName: # ALL # skip None
            # print(f'@{BM.LINE()}  appending nextName={nextName}')
            names.append(nextName)
        self.ns_names = names


@dataclass
class ASMultiname:
    kind: MultinameKind
    ns_ix: Optional[ABCNamespaceIndex] = None           # index into cp namespaces
    nam_ix: Optional[ABCStringIndex] = None             # index into cp strings
    ns_set_ix: Optional[ABCNamespaceSetIndex] = None    # index into cp ns_sets
    q_nam_ix: Optional[ABCMultinameIndex] = None        # index into cp multinames
    type_ixs: Optional[List[ABCMultinameIndex]] = None

    def getNameFromStack(self) -> bool:
      return self.kind in (MultinameKind.RTQ_NAME_L, MultinameKind.RTQ_NAME_LA, MultinameKind.MULTINAME_L, MultinameKind.MULTINAME_LA )
    def getNamespaceFromStack(self) -> bool:
      return self.kind in (MultinameKind.RTQ_NAME, MultinameKind.RTQ_NAME_A, MultinameKind.RTQ_NAME_L, MultinameKind.RTQ_NAME_LA)

    def __init__(self, reader: MemoryViewReader):
        DEBUG_self_nam_ix = 61
        self.kind = MultinameKind(reader.read_u8())
        # print(f'ASMultiname.__init__; self.kind={self.kind}')
        if self.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A): # QName -> ns_ix & nam_ix
            self.ns_ix = reader.read_int()
            self.nam_ix = reader.read_int()
            if self.nam_ix == DEBUG_self_nam_ix:
              print(f'@{BM.LINE()} ASMultiname.__init__; self.kind={self.kind} = Q_NAME[_A]; self.ns_ix={self.ns_ix}, self.nam_ix={self.nam_ix}')
        elif self.kind in (MultinameKind.RTQ_NAME, MultinameKind.RTQ_NAME_A): # RTQName -> nam_ix here (and ns from stack at R/T)
            self.nam_ix = reader.read_int()
            if self.nam_ix == DEBUG_self_nam_ix:
              print(f'@{BM.LINE()} ASMultiname.__init__; self.kind={self.kind} = RTQ_NAME_A; self.nam_ix={self.nam_ix}')
        elif self.kind in (MultinameKind.RTQ_NAME_L, MultinameKind.RTQ_NAME_LA): # RTQNameL -> (nam & ns from stack at R/T)
            # print(f'@{BM.LINE()} = RTQ_NAME_LA')
            pass
        elif self.kind in (MultinameKind.MULTINAME, MultinameKind.MULTINAME_A): # Multiname -> nam_ix & ns_set_ix
            self.nam_ix = reader.read_int()
            self.ns_set_ix = reader.read_int()
            assert self.ns_set_ix != 0, 'ns_set_ix cannot be 0'
            if self.nam_ix == DEBUG_self_nam_ix:
              print(f'@{BM.LINE()} ASMultiname.__init__; self.kind={self.kind} = MULTINAME[_A]; self.nam_ix={self.nam_ix}, self.ns_set_ix={self.ns_set_ix}')
        elif self.kind in (MultinameKind.MULTINAME_L, MultinameKind.MULTINAME_LA):# MultinameL -> ns_set_ix (nam from stack at R/T)
            self.ns_set_ix = reader.read_int()
            assert self.ns_set_ix != 0, 'ns_set_ix cannot be 0'
            # print(f'@{BM.LINE()} = MULTINAME_L[A]; self.ns_set_ix={self.ns_set_ix}')
        elif self.kind == MultinameKind.TYPE_NAME: # ??
            self.q_nam_ix = reader.read_int()
            self.type_ixs = read_array(reader, MemoryViewReader.read_int)
            # print(f'@{BM.LINE()} = TYPE_NAME; self.q_nam_ix={self.q_nam_ix}, self.type_ixs={type_ixs}')
        else:
            print(f'@{BM.LINE()} ASMultiname.__init__; self.kind={self.kind} FAILING')
            assert False, 'unreachable code'

    def DEBUG_Q_N(self, constant_pool: ASConstantPool, ns_ix) -> str:
      ns = constant_pool.namespaces[ns_ix]
      return f'<#[{ns_ix}]>{constant_pool.strings[ns.nam_ix]}##.##<#[{self.nam_ix}]>{constant_pool.strings[self.nam_ix]}'.strip('.')

    def qualified_name(self, constant_pool: ASConstantPool) -> str:
      if False: pass
      elif self.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A):
        assert self.kind == MultinameKind.Q_NAME, self.kind
        assert self.ns_ix
        assert self.nam_ix
        namespace = constant_pool.namespaces[self.ns_ix]
        if namespace.nam_ix == 0 and namespace.kind == NamespaceKind.PRIVATE_NS:
          return '' # return empty value
        if not namespace.nam_ix: # this will become an assert failure; grab some debug info
          print(f'@{BM.LINE()} (from ../avm2/abc/type.py, having NOT found namespace.nam_ix ...)')
          print(f'@{BM.LINE()} type(namespace.nam_ix)={type(namespace.nam_ix)}, namespace.nam_ix={namespace.nam_ix}')
          print(f'@{BM.LINE()} type(namespace.kind)={type(namespace.kind)}, namespace.kind={namespace.kind}')
          print(f'@{BM.LINE()} type(self.ns_ix)={type(self.ns_ix)}, self.ns_ix={self.ns_ix}')
          print(f'@{BM.LINE()} type(constant_pool.namespaces)={type(constant_pool.namespaces)}, #={len(constant_pool.namespaces)}')  #, constant_pool.namespaces={constant_pool.namespaces}')
          for ns in sorted(constant_pool.namespaces, key=lambda x: x.nam_ix if x else 0):
            if ns is None:
              col = Fore.RED
            elif ns.nam_ix == self.ns_ix:
              col = Fore.GREEN
            elif abs(ns.nam_ix - self.ns_ix) < 10:
              col = Fore.YELLOW
            else:
              col = Style.RESET_ALL
            qn = ASMultiname.DEBUG_Q_N(self, constant_pool, self.ns_ix)
            print(f'{col}@{BM.LINE()} type(ns)={type(ns)}, ns={ns}{Style.RESET_ALL}, qn={qn}')
          print(f'@{BM.LINE()} type(namespace)={type(namespace)}, namespace={namespace}')
          print(f'@{BM.LINE()} .. about to crash on <assert namespace.nam_ix> ..')
        assert namespace.nam_ix
        return f'{constant_pool.strings[namespace.nam_ix]}.{constant_pool.strings[self.nam_ix]}'.strip('.')
      else:
        assert False, f'@{BM.LINE()} MultinameKind {self.kind} not implemented .. yet'
@dataclass
class ASMultinameBis(ASMultiname):
    ixCP: int = None
    ns_name: str = None
    nam_name: str = None
    ns_set_names: List[str] = None
    q_nam_name:str = None
    # ?? # type_ixs: Optional[List[ABCMultinameIndex]] = None

    def __init__(self, rhs: ASMultiname, listStrings: List[str], listNamespaces: List[ASNamespaceBis], listNSSets: List[ASNamespaceSetsBis], ixCP: int):
      self.kind = rhs.kind
      self.ns_ix = rhs.ns_ix
      self.nam_ix = rhs.nam_ix
      self.ns_set_ix = rhs.ns_set_ix
      self.q_nam_ix = rhs.q_nam_ix
      self.type_ixs = rhs.type_ixs
      self.ixCP = ixCP
      self.ns_name = None if self.ns_ix is None else listNamespaces[self.ns_ix].nam_name
      self.nam_name = None if self.nam_ix is None else listStrings[self.nam_ix]
      self.ns_set_names = None if self.ns_set_ix is None else f'!! ## TODO @{BM.LINE(False)} !!'
      self.q_nam_name = None if self.q_nam_ix is None else f'!! ## TODO @{BM.LINE(False)} !!'
      pass
      #print(f'@{BM.LINE()} ASMultiname.__init__; self.kind={self.kind} FAILING')
      #assert False, 'unreachable code'

@dataclass
class ASMethod:
    param_count: int
    return_typ_ix: ABCMultinameIndex
    param_typ_ixs: List[ABCMultinameIndex]
    nam_ix: ABCStringIndex
    flags: MethodFlags
    options: Optional[List[ASOptionDetail]] = None
    param_nam_ixs: Optional[List[ABCStringIndex]] = None

    def __init__(self, reader: MemoryViewReader):
        self.param_count = reader.read_int()
        self.return_typ_ix = reader.read_int()
        self.param_typ_ixs = read_array(reader, MemoryViewReader.read_int, self.param_count)
        self.nam_ix = reader.read_int()
        self.flags = MethodFlags(reader.read_u8())
        if MethodFlags.HAS_OPTIONAL in self.flags:
            self.options = read_array(reader, ASOptionDetail)
        if MethodFlags.HAS_PARAM_NAMES in self.flags:
            self.param_nam_ixs = read_array(reader, MemoryViewReader.read_int, self.param_count)


@dataclass
class ASOptionDetail:
    value: int
    kind: ConstantKind

    def __init__(self, reader: MemoryViewReader):
        self.value = reader.read_int()
        self.kind = ConstantKind(reader.read_u8())


@dataclass
class ASMetadata:
    nam_ix: ABCStringIndex
    items: List[ASItem]

    def __init__(self, reader: MemoryViewReader):
        self.nam_ix = reader.read_int()
        self.items = read_array(reader, ASItem)


@dataclass
class ASItem:
    key_ix: ABCStringIndex
    value_ix: ABCStringIndex

    def __init__(self, reader: MemoryViewReader):
        self.key_ix = reader.read_int()
        self.value_ix = reader.read_int()


@dataclass
class ASInstance:
    nam_ix: ABCMultinameIndex
    super_nam_ix: ABCMultinameIndex
    flags: ClassFlags
    interface_indices: List[ABCMultinameIndex]
    init_ix: ABCMethodIndex
    traits: List[ASTrait]
    protected_namespace_index: Optional[ABCNamespaceIndex] = None

    def __init__(self, reader: MemoryViewReader):
        self.nam_ix = reader.read_int()
        self.super_nam_ix = reader.read_int()
        self.flags = ClassFlags(reader.read_u8())
        if ClassFlags.PROTECTED_NS in self.flags:
            self.protected_namespace_index = reader.read_int()
        self.interface_indices = read_array(reader, MemoryViewReader.read_int)
        self.init_ix = reader.read_int()
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASTrait:
    nam_ix: ABCMultinameIndex
    kind: TraitKind
    attributes: TraitAttributes
    data: Union[ASTraitSlot, ASTraitClass, ASTraitFunction, ASTraitMethod]
    metadata: Optional[List[ABCMetadataIndex]] = None

    def __init__(self, reader: MemoryViewReader):
        self.nam_ix = reader.read_int()
        kind = reader.read_u8()
        self.kind = TraitKind(kind & 0x0F)
        self.attributes = TraitAttributes(kind >> 4)
        if self.kind in (TraitKind.SLOT, TraitKind.CONST):
            self.data = ASTraitSlot(reader)
        elif self.kind == TraitKind.CLASS:
            self.data = ASTraitClass(reader)
        elif self.kind == TraitKind.FUNCTION:
            self.data = ASTraitFunction(reader)
        elif self.kind in (TraitKind.METHOD, TraitKind.GETTER, TraitKind.SETTER):
            self.data = ASTraitMethod(reader)
        else:
            assert False, 'unreachable code'
        if TraitAttributes.METADATA in self.attributes:
            self.metadata = read_array(reader, MemoryViewReader.read_int)


@dataclass
class ASTraitSlot:
    slot_id: int
    type_name_index: ABCMultinameIndex
    vindex: int
    vkind: Optional[ConstantKind] = None

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.type_name_index = reader.read_int()
        self.vindex = reader.read_int()
        if self.vindex:
            self.vkind = ConstantKind(reader.read_u8())


@dataclass
class ASTraitClass:
    slot_id: int
    class_ix: ABCClassIndex

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.class_ix = reader.read_int()


@dataclass
class ASTraitFunction:
    slot_id: int
    function_ix: ABCMethodIndex

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.function_ix = reader.read_int()


@dataclass
class ASTraitMethod:
    disposition_id: int
    method_ix: ABCMethodIndex

    def __init__(self, reader: MemoryViewReader):
        self.disposition_id = reader.read_int()
        self.method_ix = reader.read_int()


@dataclass
class ASClass:
    init_ix: ABCMethodIndex
    traits: List[ASTrait]

    def __init__(self, reader: MemoryViewReader):
        self.init_ix = reader.read_int()
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASScript:
    init_ix: ABCMethodIndex
    traits: List[ASTrait]

    def __init__(self, reader: MemoryViewReader):
        self.init_ix = reader.read_int()
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASMethodBody:
    method_ix: ABCMethodIndex
    max_stack: int
    local_count: int
    init_scope_depth: int
    max_scope_depth: int
    code: memoryview
    exceptions: List[ASException]
    traits: List[ASTrait]

    def __init__(self, reader: MemoryViewReader):
        self.method_ix = reader.read_int()
        self.max_stack = reader.read_int()
        self.local_count = reader.read_int()
        self.init_scope_depth = reader.read_int()
        self.max_scope_depth = reader.read_int()
        self.code = reader.read(reader.read_int())
        self.exceptions = read_array(reader, ASException)
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASException:
    from_: int
    to: int
    target: int
    exc_typ_ix: ABCStringIndex
    var_nam_ix: ABCStringIndex

    def __init__(self, reader: MemoryViewReader):
        self.from_ = reader.read_int()
        self.to = reader.read_int()
        self.target = reader.read_int()
        self.exc_typ_ix = reader.read_int()
        self.var_nam_ix = reader.read_int()
