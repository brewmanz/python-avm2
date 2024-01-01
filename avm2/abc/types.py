from __future__ import annotations

import BrewMaths as BM # export PYTHONPATH="${PYTHONPATH}:/home/bryan/git/BDL/CodeFrags/PythonBits/"

from dataclasses import dataclass
from functools import partial
from typing import Optional, List, Union, NewType

from colorama import Fore, Style

import math
import BrewMaths as BM
import type_enforced # pip install type_enforced

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

        # now call propagateStrings() to update classes with names of things

    #print(f'## @{BM.LINE()} {BM.TERM_GRN()}{BM.FUNC_NAME()}{BM.TERM_RESET()} being run ##')

    def propagateStrings(self, callerInfo: str):
      print(f'@{BM.LINE()} {BM.TERM_YLW()}{BM.FUNC_NAME()}{BM.TERM_RESET()} running (called from {callerInfo}) ... ')
      self.constant_pool._propagateStrings(callerInfo)

      # classes
      bagNumbers = [item.init_ix for item in self.classes]
      numberStats = BM.NullNanZeroMinMax(bagNumbers)
      print(f'@{BM.LINE()}  type(classes[-1])={type(self.classes[-1])} stats cinit(init_ix)={numberStats}')
      firstClassWithTraits_orNull = next((it for it in self.classes if len(it.traits) > 0), None)
      if firstClassWithTraits_orNull:
        print(f'@{BM.LINE()}  type(firstClassWithTraits_orNull.traits[-1])={type(firstClassWithTraits_orNull.traits[-1])}')
      newItemT = None # trait - just in case there are none
      newItemTS = None # traitSlot - just in case there are none
      newItemTM = None # traitMethod - just in case there are none
      newItemTG = None # traitGetter - just in case there are none
      newItemTS = None # traitSetter - just in case there are none
      newItemTC = None # traitClass - just in case there are none
      newItemTF = None # traitFunction - just in case there are none
      newItemTK = None # traitConst - just in case there are none
      for ix in range(len(self.classes)):
        item = self.classes[ix]
        if item != None:
          newItem = ASClassBis(item, self.constant_pool, ix)
          for ixT in range(len(item.traits)):
            itemT = newItem.traits[ixT]
            newItemT = ASTraitBis(itemT, self.constant_pool, ixT)
            newItem.traits[ixT] = newItemT

          self.classes[ix] = newItem
      print(f'@{BM.LINE()}  type(classes[*].trait[*])={type(newItemT)} {"" if newItemT else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(classes[*].traitS[*])={type(newItemTS)} {"" if newItemTS else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(classes[*].traitM[*])={type(newItemTM)} {"" if newItemTM else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(classes[*].traitG[*])={type(newItemTG)} {"" if newItemTG else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(classes[*].traitS[*])={type(newItemTS)} {"" if newItemTS else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(classes[*].traitC[*])={type(newItemTC)} {"" if newItemTC else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(classes[*].traitF[*])={type(newItemTF)} {"" if newItemTF else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(classes[*].traitK[*])={type(newItemTK)} {"" if newItemTK else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(classes[-1])={type(self.classes[-1])} #={len(self.classes)}')
      firstClassWithTraits_orNull = next((it for it in self.classes if len(it.traits) > 0), None)
      if firstClassWithTraits_orNull:
        print(f'@{BM.LINE()}  type(firstClassWithTraits_orNull.traits[-1])={type(firstClassWithTraits_orNull.traits[-1])}')

      # instances
      bagNumbers = [item.init_ix for item in self.instances]
      numberStats = BM.NullNanZeroMinMax(bagNumbers)
      print(f'@{BM.LINE()}  type(instances[-1])={type(self.instances[-1])}, stats iinit(init_ix)={numberStats}')
      newItemT = None # trait - just in case there are none
      newItemTS = None # traitSlot - just in case there are none
      newItemTM = None # traitMethod - just in case there are none
      newItemTG = None # traitGetter - just in case there are none
      newItemTS = None # traitSetter - just in case there are none
      newItemTC = None # traitClass - just in case there are none
      newItemTF = None # traitFunction - just in case there are none
      newItemTK = None # traitConst - just in case there are none
      for ix in range(len(self.instances)):
        item = self.instances[ix]
        if item != None:
          newItem = ASInstanceBis(item, self.constant_pool, ix)
          # propagate instance names into class objects
          self.classes[ix].nam_name = newItem.nam_name
          self.classes[ix].super_name = newItem.super_name

          # update traits
          for ixT in range(len(item.traits)):
            itemT = newItem.traits[ixT]
            newItemT = ASTraitBis(itemT, self.constant_pool, ixT)
            newItem.traits[ixT] = newItemT

          self.instances[ix] = newItem
      print(f'@{BM.LINE()}  type(instances[*].trait[*])={type(newItemT)} {"" if newItemT else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(instances[*].traitS[*])={type(newItemTS)} {"" if newItemTS else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(instances[*].traitM[*])={type(newItemTM)} {"" if newItemTM else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(instances[*].traitG[*])={type(newItemTG)} {"" if newItemTG else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(instances[*].traitS[*])={type(newItemTS)} {"" if newItemTS else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(instances[*].traitC[*])={type(newItemTC)} {"" if newItemTC else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(instances[*].traitF[*])={type(newItemTF)} {"" if newItemTF else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(instances[*].traitK[*])={type(newItemTK)} {"" if newItemTK else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(instances[-1])={type(self.instances[-1])}')

      # methods
      print(f'@{BM.LINE()}  type(methods[-1])={type(self.methods[-1])} #={len(self.methods)}')
      for ix in range(len(self.methods)):
        item = self.methods[ix]
        if item != None:
          newItem = ASMethodBis(item, self.constant_pool, ix)
          self.methods[ix] = newItem
      print(f'@{BM.LINE()}  type(methods[-1])={type(self.methods[-1])} #={len(self.methods)}')

      # propagate instance-trait-method names back to methods
      for item in self.instances:
        for trait in item.traits:
          if isinstance(trait.data, ASTraitMethod):
            traitM: ASTraitMethod = trait.data
            ixMethod = traitM.method_ix
            itemM = self.methods[ixMethod]
            assert isinstance(itemM, ASMethodBis)
            assert itemM, f'itemM is None'
            # sometimes, one method can be 'handler_stageResize' and 'heroes.handler_stageResize'
            if trait.nam_name in itemM.nam_name: continue # leave as-is; old either exact or longer version of name
            if itemM.nam_name in trait.nam_name: # if new name is longer than old name: update it
              itemM.nam_name = trait.nam_name # name comes from trait, if traitM used
              continue
            # assert False, f'itemM.nam_name not empty or match but {itemM.nam_name}; was going to set it to {trait.nam_name}'

      # method_bodies
      bagNumbers = [item.method_ix for item in self.method_bodies]
      numberStats = BM.NullNanZeroMinMax(bagNumbers)
      print(f'@{BM.LINE()}  type(method_bodies[-1])={type(self.method_bodies[-1])}, stats method_ix={numberStats}')
      newItemE = None # exception - just in case there are none
      newItemT = None # trait - just in case there are none
      newItemTS = None # traitSlot - just in case there are none
      newItemTM = None # traitMethod - just in case there are none
      newItemTG = None # traitGetter - just in case there are none
      newItemTS = None # traitSetter - just in case there are none
      newItemTC = None # traitClass - just in case there are none
      newItemTF = None # traitFunction - just in case there are none
      newItemTK = None # traitConst - just in case there are none
      for ix in range(len(self.method_bodies)):
        item = self.method_bodies[ix]
        if item != None:
          newItem = ASMethodBodyBis(item, self.constant_pool, ix)
          # back-populate method.ixBody
          method = self.methods[item.method_ix]
          if isinstance(method, ASMethodBis):
            assert method.ixBody == None
            method.ixBody = ix
          # update exceptions
          for ixE in range(len(item.exceptions)):
            newItemE = ASExceptionBis(item.exceptions[ixE], self.constant_pool, ixE)
            newItem.exceptions[ixE] = newItemE
          # update traits
          for ixT in range(len(item.traits)):
            newItemT = ASTraitBis(item.traits[ixT], self.constant_pool, ixT)
            newItem.traits[ixT] = newItemT
          self.method_bodies[ix] = newItem
      print(f'@{BM.LINE()}  type(method_bodies[*].exceptions[*])={type(newItemE)}')
      print(f'@{BM.LINE()}  type(method_bodies[*].traits[*])={type(newItemT)}')
      print(f'@{BM.LINE()}  type(method_bodies[*].traitS[*])={type(newItemTS)} {"" if newItemTS else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(method_bodies[*].traitM[*])={type(newItemTM)} {"" if newItemTM else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(method_bodies[*].traitG[*])={type(newItemTG)} {"" if newItemTG else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(method_bodies[*].traitS[*])={type(newItemTS)} {"" if newItemTS else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(method_bodies[*].traitC[*])={type(newItemTC)} {"" if newItemTC else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(method_bodies[*].traitF[*])={type(newItemTF)} {"" if newItemTF else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(method_bodies[*].traitK[*])={type(newItemTK)} {"" if newItemTK else "TODO NONE FOUND"}')
      print(f'@{BM.LINE()}  type(method_bodies[-1])={type(self.method_bodies[-1])}')

      # scripts
      bagNumbers = [item.init_ix for item in self.scripts]
      numberStats = BM.NullNanZeroMinMax(bagNumbers)
      print(f'@{BM.LINE()}  type(scripts[-1])={type(self.scripts[-1])}, stats init_ix={numberStats}')

@dataclass
class ASConstantPool: # cpool_info
    integers: List[int] # u30 int_count + s32 integer[int_count]
    unsigned_integers: List[int] # u30 uint_count + u32 uinteger[uint_count]
    doubles: List[float] # u30 double_count + d64 double[double_count]
    strings: List[str] # u30 string_count + string_info string[string_count]
    namespaces: List[ASNamespace] # u30 namespace_count + namespace_info namespace[namespace_count]
    ns_sets: List[ASNamespaceSet] # u30 ns_set_count + ns_set_info ns_set[ns_set_count]
    multinames: List[ASMultiname] # u30 multiname_count + multiname_info multiname[multiname_count]
    cbNotifications = None

    def __init__(self, reader: MemoryViewReader):
        self.integers = read_array_with_default(reader, partial(MemoryViewReader.read_int, unsigned=False), 0)
        self.unsigned_integers = read_array_with_default(reader, MemoryViewReader.read_int, 0)
        self.doubles = read_array_with_default(reader, MemoryViewReader.read_d64, math.nan)
        self.strings = read_array_with_default(reader, read_string, None)
        self.namespaces = read_array_with_default(reader, ASNamespace, None)
        self.ns_sets = read_array_with_default(reader, ASNamespaceSet, None)
        self.multinames = read_array_with_default(reader, ASMultiname, None)
        self.cbNotifications = None

    def _propagateStrings(self, callerInfo: str):
      print(f'@{BM.LINE()} cp _propagateStrings running (called from {callerInfo}) ... ')

      print(f'@{BM.LINE()}  type(strings[-1])={type(self.strings[-1])} #={len(self.strings)}')

      print(f'@{BM.LINE()}  type(namespaces[-1])={type(self.namespaces[-1])} #={len(self.namespaces)}')
      for ix in range(len(self.namespaces)):
        item = self.namespaces[ix]
        if item != None:
          newItem = ASNamespaceBis(item, self, ix)
          self.namespaces[ix] = newItem
      print(f'@{BM.LINE()}  type(namespaces[-1])={type(self.namespaces[-1])} #={len(self.namespaces)}')

      print(f'@{BM.LINE()}  type(ns_sets[-1])={type(self.ns_sets[-1])} #={len(self.ns_sets)}')
      for ix in range(len(self.ns_sets)):
        item = self.ns_sets[ix]
        if item != None:
          newItem = ASNamespaceSetBis(item, self, ix)
          self.ns_sets[ix] = newItem
      print(f'@{BM.LINE()}  type(ns_sets[-1])={type(self.ns_sets[-1])} #={len(self.ns_sets)}')

      print(f'@{BM.LINE()}  type(multinames[-1])={type(self.multinames[-1])} #={len(self.multinames)}')
      for ix in range(len(self.multinames)):
        item = self.multinames[ix]
        if item != None:
          newItem = ASMultinameBis(item, self, ix)
          self.multinames[ix] = newItem
      print(f'@{BM.LINE()}  type(multinames[-1])={type(self.multinames[-1])} #={len(self.multinames)}')

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

    def __init__(self, rhs: ASNamespace, constant_pool: ASConstantPool, ixCP: int):
        self.kind = rhs.kind
        self.nam_ix = rhs.nam_ix
        self.ixCP = ixCP
        if rhs.nam_ix > 0 and rhs.nam_ix < len(constant_pool.strings):
          self.nam_name = constant_pool.strings[rhs.nam_ix]
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

    def __init__(self, rhs: ASNamespaceSet, constant_pool: ASConstantPool, ixCP: int):
        self.namespaces = rhs.namespaces
        self.ixCP = ixCP
        names = list()
        for ix in range(len(self.namespaces)):
          ixNS = self.namespaces[ix]
          ns = constant_pool.namespaces[ixNS]
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
          if constant_pool.cbNotifications:
            constant_pool.cbNotifications(f'@{BM.LINE()} {BM.FUNC_NAME()} namespace.nam_ix has no value for {self}')
          # vvvv DEBUG INFO
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
          print(f'@{BM.LINE()} .. {BM.TERM_WHT_ON_RED()}{BM.FUNC_NAME()} about to crash on <assert namespace.nam_ix> ..{BM.TERM_RESET()}')
          # ^^^ DEBUG INFO
        assert namespace.nam_ix
        return f'{constant_pool.strings[namespace.nam_ix]}.{constant_pool.strings[self.nam_ix]}'.strip('.')
      elif self.kind == MultinameKind.TYPE_NAME:
        refMultiName = constant_pool.multinames[self.q_nam_ix]
        qn = f'!! RESOLVE q_nam_ix={self.q_nam_ix}=>{refMultiName.nam_name} type_ixs={self.type_ixs} !!'
        msg = f'@{BM.LINE()} {BM.TERM_WHT_ON_RED()}{BM.FUNC_NAME()} EXPERIMENTAL MultinameKind TYPE_NAME; q_nam_ix={self.q_nam_ix} qn={qn}{BM.TERM_RESET()}'
        #print(msg)
        if constant_pool.cbNotifications:
          constant_pool.cbNotifications(msg)
        return f'{self.ns_name}.{self.nam_name}'.strip('.')
        #return qn
      else:
        if constant_pool.cbNotifications:
          constant_pool.cbNotifications(f'@{BM.LINE()} {BM.FUNC_NAME()} UNEXPECTED MultinameKind {self.kind}(x{self.kind:02x}) not implemented)')
        # vvvv DEBUG INFO
        print(f'@{BM.LINE()} {BM.TERM_WHT_ON_RED()}{BM.FUNC_NAME()} (from ../avm2/abc/type.py, having UNEXPECTED MultinameKind {self.kind}(x{self.kind:02x}) not implemented){BM.TERM_RESET()}')
        print(f'@{BM.LINE()} self={self}')
        print(f'@{BM.LINE()} .. {BM.TERM_WHT_ON_RED()}{BM.FUNC_NAME()} about to crash on assert False ..{BM.TERM_RESET()}')
        # ^^^ DEBUG INFO
        assert False, f'@{BM.LINE()} MultinameKind {self.kind} not implemented .. yet. TYPE_NAME={MultinameKind.TYPE_NAME}' # 29 =
@dataclass
class ASMultinameBis(ASMultiname):
    ixCP: int = None
    ns_name: str = None
    nam_name: str = None
    ns_set_names: List[str] = None
    q_nam_name:str = None
    # ?? # type_ixs: Optional[List[ABCMultinameIndex]] = None

    #def __init__(self, rhs: ASMultiname, listStrings: List[str], listNamespaces: List[ASNamespaceBis], listNSSets: List[ASNamespaceSetsBis], ixCP: int):
    def __init__(self, rhs: ASMultiname, constant_pool: ASConstantPool, ixCP: int):
      self.kind = rhs.kind
      self.ns_ix = rhs.ns_ix
      self.nam_ix = rhs.nam_ix
      self.ns_set_ix = rhs.ns_set_ix
      self.q_nam_ix = rhs.q_nam_ix
      self.type_ixs = rhs.type_ixs
      self.ixCP = ixCP
      self.ns_name = None if self.ns_ix is None else constant_pool.namespaces[self.ns_ix].nam_name #listNamespaces[self.ns_ix].nam_name
      self.nam_name = None if self.nam_ix is None else constant_pool.strings[self.nam_ix] #listStrings[self.nam_ix]
      self.ns_set_names = None if self.ns_set_ix is None else f'!! ## TODO @{BM.LINE(False)} {constant_pool.ns_sets[self.ns_set_ix].ns_names}'

      # TYPE_NAME handling
      if self.q_nam_ix:
        qMultiName = constant_pool.multinames[self.q_nam_ix]
        q_nam_name = qMultiName.nam_name
        q_ns_name = qMultiName.ns_name
        self.q_nam_name = None if self.q_nam_ix is None else f'!! ## TODO @{BM.LINE(False)} ns={q_ns_name} nam={q_nam_name} t_ixs={self.type_ixs}'
        if self.nam_name == None:
          self.nam_name = q_nam_name
        if self.ns_name == None:
          self.ns_name = q_ns_name
      else:
        self.q_nam_name = None


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
class ASMethodBis(ASMethod):
    ixABC: ABCMethodIndex = None
    ixBody: ABCMethodBodyIndex = None # Method to MethodBody
    methodType: str = None # e.g. class init, instance init
    return_typ_name: str = None
    param_typ_names: List[str] = None
    nam_name: str = None
    param_nam_names: List[str] = None

    def __init__(self, rhs: ASMethod, constant_pool: ASConstantPool, ixABC: int):
        self.param_count = rhs.param_count
        self.return_typ_ix = rhs.return_typ_ix
        self.param_typ_ixs = rhs.param_typ_ixs
        self.nam_ix = rhs.nam_ix
        self.flags = rhs.flags
        self.options = rhs.options
        self.param_nam_ixs = rhs.param_nam_ixs

        self.ixABC = ixABC
        self.ixBody = None
        self.methodType = None

        key = self.return_typ_ix
        self.return_typ_name = constant_pool.multinames[key].qualified_name(constant_pool) if key else None

        self.param_typ_names = list()
        if self.param_typ_ixs:
          for ix in range(len(self.param_typ_ixs)):
            key = self.param_typ_ixs[ix]
            param_typ_name = constant_pool.multinames[key].qualified_name(constant_pool) if key else None
            self.param_typ_names.append(param_typ_name)

        key = self.nam_ix
        if key is None:
          nam_name = None
        else:
          nam_name = '' if key == 0 else constant_pool.strings[key]
        self.nam_name = nam_name

        self.param_nam_names = None
        if self.flags:
          if MethodFlags.HAS_PARAM_NAMES in self.flags:
            self.param_nam_names = list()
            for ix in range(len(self.param_nam_ixs)):
              key = self.param_nam_ixs[ix]
              param_nam_name = constant_pool.strings[key] if key else None
              self.param_nam_names.append(param_nam_name)


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
    init_ix: ABCMethodIndex # u30 iinit; index into abcFile.method array
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
class ASInstanceBis(ASInstance):
    ixABC: int = None
    nam_name: str = None
    super_name: str = None

    def __init__(self, rhs: ASInstance, constant_pool: ASConstantPool, ixABC: int):
        self.nam_ix = rhs.nam_ix
        self.super_nam_ix = rhs.super_nam_ix
        self.flags = rhs.flags
        self.interface_indices = rhs.interface_indices
        self.init_ix = rhs.init_ix
        self.traits = rhs.traits
        self.protected_namespace_index = rhs.protected_namespace_index

        self.ixABC = ixABC
        self.nam_name = constant_pool.multinames[self.nam_ix].qualified_name(constant_pool)
        if self.super_nam_ix > 0:
          self.super_name = constant_pool.multinames[self.super_nam_ix].qualified_name(constant_pool)


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
class ASTraitBis(ASTrait):
    ixT: int = None
    nam_name: str = None

    def __init__(self, rhs: ASTrait, constant_pool: ASConstantPool, ixT: int):
        self.nam_ix = rhs.nam_ix
        self.kind = rhs.kind
        self.attributes = rhs.attributes
        self.data = rhs.data
        self.metadata = rhs.metadata

        self.ixT = ixT
        self.nam_name = constant_pool.multinames[self.nam_ix].qualified_name(constant_pool)
        if self.nam_name[:5] != 'http:':
          assert not '/' in self.nam_name, f'@{BM.LINE(False)} self.nam_ix={self.nam_ix}, self.nam_name = {self.nam_name}'
          #assert not ':' in self.nam_name, f'@{BM.LINE(False)} self.nam_ix={self.nam_ix}, self.nam_name = {self.nam_name}'

def GetNameOfTraitVindexVkind(vindex: int, vkind: Optional[ConstantKind]) -> str:
  pass

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
class ASTraitSlotBis(ASTraitSlot):
  ixT: int = None
  type_name_name: str = None
  vname: str = None
  def __init__(self, rhs: ASTrait, constant_pool: ASConstantPool, ixT: int):
    self.slot_id = rhs.slot_id
    self.type_name_index = rhs.type_name_index
    self.vindex = rhs.vindex
    self.vkind = rhs.vkind

    self.ixT = ixT
    self.nam_name = constant_pool.multinames[self.nam_ix].qualified_name(constant_pool)

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
    nam_name: str # not available at creation time
    super_name: str # not available at creation time
    init_ix: ABCMethodIndex # u30 cinit
    traits: List[ASTrait] # u30 trait_count + traits_info traits[trait_count]

    def __init__(self, reader: MemoryViewReader):
        self.nam_name = None # will be gleaned from instances later
        self.super_name = None # will be gleaned from instances later
        self.init_ix = reader.read_int()
        self.traits = read_array(reader, ASTrait)
@dataclass
class ASClassBis(ASClass):
    ixABC: int = None
    def __init__(self, rhs: ASClass, constant_pool: ASConstantPool, ixABC: int):
        self.nam_name = rhs.nam_name
        self.super_name = rhs.super_name
        self.init_ix = rhs.init_ix
        self.traits = rhs.traits

        self.ixABC = ixABC

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
class ASMethodBodyBis(ASMethodBody):
    ixABC: int = None
    def __init__(self, rhs: ASMethodBody, constant_pool: ASConstantPool, ixABC: int):
        self.method_ix = rhs.method_ix
        self.max_stack = rhs.max_stack
        self.local_count = rhs.local_count
        self.init_scope_depth = rhs.init_scope_depth
        self.max_scope_depth = rhs.max_scope_depth
        self.code = rhs.code
        self.exceptions = rhs.exceptions
        self.traits = rhs.traits

        self.ixABC = ixABC


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

@dataclass
class ASExceptionBis(ASException):
  ixMB: int = None
  exc_typ_name: str = None
  var_nam_name: str = None
  def __init__(self, rhs: ASException, constant_pool: ASConstantPool, ixMB: int):
    self.from_ = rhs.from_
    self.to = rhs.to
    self.target = rhs.target
    self.exc_typ_ix = rhs.exc_typ_ix
    self.var_nam_ix = rhs.var_nam_ix

    self.ixMB = ixMB
    self.exc_typ_name = constant_pool.strings[self.exc_typ_ix]
    self.var_nam_name = constant_pool.strings[self.var_nam_ix]
