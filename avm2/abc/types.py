from __future__ import annotations

import BrewMaths as BM # export PYTHONPATH="${PYTHONPATH}:/home/bryan/git/BDL/CodeFrags/PythonBits/"

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
class ABCFile: # abcfile
    minor_version: int # u16 minor_version
    major_version: int # u16 major_version
    constant_pool: ASConstantPool # cpool_info constant_pool
    methods: List[ASMethod] # u30 method_count + method_info method[method_count]
    metadata: List[ASMetadata] # u30 metadata_count + metadata_info metadata[metadata_count]
    instances: List[ASInstance] # u30 class_count + instance_info instance[class_count]
    classes: List[ASClass] # class_info class[class_count]
    scripts: List[ASScript] # u30 script_count + script_info script[script_count]
    method_bodies: List[ASMethodBody] # u30 method_body_count + method_body_info method_body[method_body_count]

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
class ASConstantPool: # cpool_info
    integers: List[int] # u30 int_count + s32 integer[int_count]
    unsigned_integers: List[int] # u30 uint_count + u32 uinteger[uint_count]
    doubles: List[float] # u30 double_count + d64 double[double_count]
    strings: List[str] # u30 string_count + string_info string[string_count]
    namespaces: List[ASNamespace] # u30 namespace_count + namespace_info namespace[namespace_count]
    ns_sets: List[ASNamespaceSet] # u30 ns_set_count + ns_set_info ns_set[ns_set_count]
    multinames: List[ASMultiname] # u30 multiname_count + multiname_info multiname[multiname_count]

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
class ASNamespace: # namespace_info
    kind: NamespaceKind # u8 kind
    nam_ix: ABCStringIndex # u30 name

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
class ASNamespaceSet: # ns_set_info
    namespaces: List[ABC/NamespaceIndex] # u30 count + u30 ns[count]

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
class ASMultiname: # multiname_info
    kind: MultinameKind # u8 kind
    ns_ix: Optional[ABCNamespaceIndex] = None           # index into cp namespaces
    nam_ix: Optional[ABCStringIndex] = None             # index into cp strings
    ns_set_ix: Optional[ABCNamespaceSetIndex] = None    # index into cp ns_sets
    q_nam_ix: Optional[ABCMultinameIndex] = None        # index into cp multinames
    type_ixs: Optional[List[ABCMultinameIndex]] = None # u8 data[]

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
class ASMethod: # method_info
    param_count: int # u30 param_count
    return_typ_ix: ABCMultinameIndex # u30 return_type
    param_typ_ixs: List[ABCMultinameIndex] # u30 param_type[param_count]
    nam_ix: ABCStringIndex # u30 name
    flags: MethodFlags # u8 flags
    options: Optional[List[ASOptionDetail]] = None # option_info options
    param_nam_ixs: Optional[List[ABCStringIndex]] = None # param_info param_names

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
class ASMethodBis:
    return_typ_name: str = None
    param_typ_names: List[str] = None
    nam_name: str = None
    param_nam_names: List[str] = None

    def __init__(self, rhs: ASMethod, constant_pool: ASConstantPool):
        self.param_count = rhs.param_count
        self.return_typ_ix = rhs.return_typ_ix
        self.param_typ_ixs = rhs.param_typ_ixs
        self.nam_ix = rhs.nam_ix
        self.flags = rhs.flags
        self.options = rhs.options
        self.param_nam_ixs = rhs.param_nam_ixs

        self.return_typ_name = constant_pool,multinames[self.return_typ_ix].qualified_name(constant_pool)
        self.param_typ_names = list()
        for ix in self.param_typ_ixs:
          self.param_typ_names.append(constant_pool,multinames[self.param_typ_ixs[ix]].qualified_name(constant_pool))

@dataclass
class ASOptionDetail: # option_detail
    value: int # u30 val
    kind: ConstantKind # u8 kind

    def __init__(self, reader: MemoryViewReader):
        self.value = reader.read_int()
        self.kind = ConstantKind(reader.read_u8())


@dataclass
class ASMetadata: # metadata_info
    nam_ix: ABCStringIndex # u30 name
    items: List[ASItem] # u30 item_count + item_info items[item_count]

    def __init__(self, reader: MemoryViewReader):
        self.nam_ix = reader.read_int()
        self.items = read_array(reader, ASItem)


@dataclass
class ASItem: # item_info
    key_ix: ABCStringIndex # u30 key
    value_ix: ABCStringIndex # u30 value

    def __init__(self, reader: MemoryViewReader):
        self.key_ix = reader.read_int()
        self.value_ix = reader.read_int()


@dataclass
class ASInstance: # instance_info
    nam_ix: ABCMultinameIndex # u30 name
    super_nam_ix: ABCMultinameIndex # u30 super_name
    flags: ClassFlags # u8 flags
    interface_indices: List[ABCMultinameIndex] # u30 intrf_count + u30 interface[intrf_count]
    init_ix: ABCMethodIndex # u30 iinit
    traits: List[ASTrait] # u30 trait_count + traits_info trait[trait_count]
    protected_namespace_index: Optional[ABCNamespaceIndex] = None # u30 protectedNs

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
class ASTrait: # traits_info
    nam_ix: ABCMultinameIndex # u30 name
    kind: TraitKind # u8 kind
    attributes: TraitAttributes
    data: Union[ASTraitSlot, ASTraitClass, ASTraitFunction, ASTraitMethod]  # u8 data[]
    metadata: Optional[List[ABCMetadataIndex]] = None # u30 metadata_count + u30 metadata[metadata_count]

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
class ASTraitSlot: # trait_slot
    slot_id: int # u30 slot_id
    type_name_index: ABCMultinameIndex # u30 type_name
    vindex: int # u30 vindex
    vkind: Optional[ConstantKind] = None # u8 vkind

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.type_name_index = reader.read_int()
        self.vindex = reader.read_int()
        if self.vindex:
            self.vkind = ConstantKind(reader.read_u8())


@dataclass
class ASTraitClass: # trait_class
    slot_id: int # u30 slot_id
    class_ix: ABCClassIndex # u30 classi

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.class_ix = reader.read_int()


@dataclass
class ASTraitFunction: # trait_function
    slot_id: int # u30 slot_id
    function_ix: ABCMethodIndex # u30 function

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.function_ix = reader.read_int()


@dataclass
class ASTraitMethod: # trait_method
    disposition_id: int # u30 disp_id
    method_ix: ABCMethodIndex # u30 method

    def __init__(self, reader: MemoryViewReader):
        self.disposition_id = reader.read_int()
        self.method_ix = reader.read_int()


@dataclass
class ASClass: # class_info
    init_ix: ABCMethodIndex # u30 cinit
    traits: List[ASTrait] # u30 trait_count + traits_info traits[trait_count]

    def __init__(self, reader: MemoryViewReader):
        self.init_ix = reader.read_int()
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASScript: # script_info
    init_ix: ABCMethodIndex # u30 init
    traits: List[ASTrait] # u30 trait_count + traits_info trait[trait_count]

    def __init__(self, reader: MemoryViewReader):
        self.init_ix = reader.read_int()
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASMethodBody: # method_body_info
    method_ix: ABCMethodIndex # u30 method
    max_stack: int # u30 max_stack
    local_count: int # u30 local_count
    init_scope_depth: int # u30 init_scope_depth
    max_scope_depth: int # u30 max_scope_depth
    code: memoryview # u30 code_length + u8 code[code_length]
    exceptions: List[ASException] # u30 exception_count + exception_info exception[exception_count]
    traits: List[ASTrait] # u30 trait_count + traits_info trait[trait_count]

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
class ASException: # exception_info
    from_: int # u30 from
    to: int # u30 to
    target: int # u30 target
    exc_typ_ix: ABCStringIndex # u30 exc_type
    var_nam_ix: ABCStringIndex # u30 var_name

    def __init__(self, reader: MemoryViewReader):
        self.from_ = reader.read_int()
        self.to = reader.read_int()
        self.target = reader.read_int()
        self.exc_typ_ix = reader.read_int()
        self.var_nam_ix = reader.read_int()
