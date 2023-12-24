from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, DefaultDict, Dict, Iterable, List, Tuple, Union

import avm2.abc.instructions
from avm2.abc.enums import ConstantKind, MethodFlags, TraitKind
from avm2.abc.types import (
    ABCClassIndex,
    ABCFile,
    ABCMethodBodyIndex,
    ABCMethodIndex,
    ABCScriptIndex,
    ASMethodBody,
)
from avm2.exceptions import ASJumpException, ASReturnException
from avm2.io import MemoryViewReader
from avm2.runtime import ASObject, ASUndefined, undefined
from avm2.swf.types import DoABCTag, Tag, TagType

import BrewMaths as BM

class VirtualMachine:
    def __init__(self, abc_file: ABCFile):
        self.abc_file = abc_file

        # extend classes (via ASxxxBis classes) and add strings
        self.abc_file.propagateStrings(BM.LINE(False))

        # Quick access.
        self.constant_pool = abc_file.constant_pool
        self.strings = self.constant_pool.strings
        self.multinames = self.constant_pool.multinames
        self.integers = self.constant_pool.integers
        self.doubles = self.constant_pool.doubles
        self.namespaces = self.constant_pool.namespaces

        # Linking.
        self.method_to_body = self.link_methods_to_bodies()
        self.class_to_script = self.link_classes_to_scripts()
        self.name_to_class = dict(self.link_names_to_classes())
        self.name_to_method = dict(self.link_names_to_methods())

        # backfill class names and
        print(f'@{BM.LINE()} !! TODO backfill ns + name to classes & methods')

        # Runtime.
        self.class_objects: DefaultDict[ABCClassIndex, ASObject] = defaultdict(ASObject)  # FIXME: unsure, prototypes?
        self.script_objects: DefaultDict[ABCScriptIndex, ASObject] = defaultdict(ASObject)  # FIXME: unsure, what is it?
        self.global_object = ASObject(BM.LINE(False), properties={
            # key seems to be tuple of (namespace, name)
            ('', 'Object'): ASObject(BM.LINE(False)),
            ('flash.utils', 'Dictionary'): ASObject(BM.LINE(False)),
        })  # FIXME: unsure, prototypes again?

        # HACK 2023-12-13 not sure how to set object properties; maybe create a dictionary? Let's see.
        # or not # self.nsObject XXX: DefaultDict[ABCClassIndex, ASObject] = defaultdict(ASObject)  # FIXME: unsure, prototypes?

        # callbacks
        self.cbOnInsExe: CallbackOnInstructionExecuting = None

        self.GDictFails = 0

    # Linking.
    # ------------------------------------------------------------------------------------------------------------------

    def link_methods_to_bodies(self) -> Dict[ABCMethodIndex, ABCMethodBodyIndex]:
        """
        Link methods and methods bodies.
        """
        return {method_body.method_ix: index for index, method_body in enumerate(self.abc_file.method_bodies)}

    def link_classes_to_scripts(self) -> Dict[ABCClassIndex, ABCScriptIndex]:
        return {
            trait.data.class_ix: script_index
            for script_index, script in enumerate(self.abc_file.scripts)
            for trait in script.traits
            if trait.kind == TraitKind.CLASS
        }

    def link_names_to_classes(self) -> Iterable[Tuple[str, ABCClassIndex]]:
        """
        Link class names and class indices.
        """
        # FIXME: this is doubtful.
        for index, instance in enumerate(self.abc_file.instances):
            assert instance.nam_ix
            yield self.multinames[instance.nam_ix].qualified_name(self.constant_pool), index

    def link_names_to_methods(self) -> Iterable[Tuple[str, ABCMethodIndex]]:
        """
        Link method names and method indices.
        """
        # FIXME: this is doubtful.
        print(F'!! @{BM.LINE()} link_names_to_methods')
        for instance, class_ in zip(self.abc_file.instances, self.abc_file.classes):
            qualified_class_name = self.multinames[instance.nam_ix].qualified_name(self.constant_pool)
            for trait in class_.traits:
                if trait.kind in (TraitKind.GETTER, TraitKind.SETTER, TraitKind.METHOD):
                    qualified_trait_name = self.multinames[trait.nam_ix].qualified_name(self.constant_pool)
                    qual_class_trait = f'{qualified_class_name}.{qualified_trait_name}'
                    # too soon # self.abc_file.methods[trait.data.method_ix].nam_name = qual_class_trait  # back-paint method name
                    yield qual_class_trait, trait.data.method_ix

    # Resolving.
    # ------------------------------------------------------------------------------------------------------------------
    def resolve_multiname(self, scopeStack: List[ASObject], name: str, namespaces: Iterable[str]) -> Tuple[ASObject, str, str, Any]:
        '''
        Returns resolved object, its name, and its namespace. Also its scopeStack entry
        If the scopeStack entry is a string, then the string IS the resolved object
        '''
        for scopeObject_ in reversed(scopeStack):
            if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)ResMulNam.sobj=<{BM.DumpVar(scopeObject_)}>')
            for namespace in namespaces:
                try:
                    return self.resolve_qname(scopeObject_, namespace, name), name, namespace, scopeObject_
                except KeyError:
                    pass
        raise KeyError(name, namespaces)

    def resolve_qname(self, scopeObject_: ASObject, namespace: str, name: str) -> Any:
        # Typically, the order of the search for resolving multinames is
        # the object’s declared traits, its dynamic properties, and finally the prototype chain.
        # TODO: declared traits.

        if isinstance(scopeObject_, str): # if a string, return as-is
          return scopeObject_
        return scopeObject_.properties[namespace, name]
        # TODO: prototype chain.

    def lookup_class(self, qualified_name: str) -> ABCClassIndex:
      try:
        return self.name_to_class[qualified_name]
      except KeyEr:
        self.GDictFails += 1
        if self.GDictFails < 5:
          print(F'!! @{BM.LINE()} n2c KeyError [{qualified_name}]')
          if self.GDictFails == 1:
            print(F'!! @{BM.LINE()} n2c Keys(#{len(self.name_to_class)}) are ...')
            for k, v in self.name_to_class.items():
              print(F'!! @{BM.LINE()} n2c Key:[{k}]>[{v}]')
        raise

    def lookup_method(self, qualified_name: str) -> ABCMethodIndex:
      try:
        return self.name_to_method[qualified_name]
      except KeyError:
        self.GDictFails += 1
        if self.GDictFails < 5:
          print(F'!! @{BM.LINE()} n2m KeyError [{qualified_name}]')
          if self.GDictFails == 1:
            print(F'!! @{BM.LINE()} n2m Keys(#{len(self.name_to_method)}) are ...')
            for k, v in self.name_to_method.items():
              print(F'!! @{BM.LINE()} n2m Key:[{k}]>[{v}]')
        raise

    # Scripts.
    # ------------------------------------------------------------------------------------------------------------------

    def init_script(self, script_index: ABCScriptIndex):
        """
        Initialise the specified script.
        """
        if script_index not in self.script_objects:
            # TODO: what is `this`?
            self.call_method(self.abc_file.scripts[script_index].init_ix, self.script_objects[script_index])

    # Classes.
    # ------------------------------------------------------------------------------------------------------------------

    def init_class(self, class_ix: ABCClassIndex):
        self.init_script(self.class_to_script[class_ix])
        self.call_method(self.abc_file.classes[class_ix].init_ix, self.class_objects[class_ix])
        # TODO: the scope stack is saved by the created ClassClosure.

    def new_instance(self, index_or_name: Union[ABCClassIndex, str], *args) -> ASObject:
        if isinstance(index_or_name, int):
            class_ix = ABCClassIndex(index_or_name)
        elif isinstance(index_or_name, str):
            class_ix = self.lookup_class(index_or_name)
        else:
            raise ValueError(index_or_name)

        instance = ASObject(BM.LINE(False), class_ix=class_ix)
        # FIXME: call super constructor?
        self.call_method(self.abc_file.instances[class_ix].init_ix, instance, *args)
        return instance

    # Execution.
    # ------------------------------------------------------------------------------------------------------------------

    def call_entry_point(self):
        """
        Call the entry point, that is the last script in ABCFile.
        """
        self.init_script(ABCScriptIndex(-1))

    def call_ClassInstanceInit(self, index_or_name: Union[ABCMethodIndex, str], *args) -> Any:
        """
        Call the specified class instance initialise method. Done for each instance
        """
        print(f'## @{BM.LINE()} ## call_static ## ...')
        if isinstance(index_or_name, int):
            index = ABCMethodIndex(index_or_name)
        elif isinstance(index_or_name, str):
            index = self.lookup_method(index_or_name)
        else:
            raise ValueError(index_or_name)
        methodInfo = self.abc_file.methods[index]
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)index_or_name={BM.DumpVar(index_or_name)} -> index {BM.DumpVar(index)} mi.n={methodInfo.nam_name}:{"(add methodInfo)"} #M2B={len(self.method_to_body)} #a.MB={len(self.abc_file.method_bodies)}')

        # TODO: init script on demand.
        ixMB = self.method_to_body[index]
        method_body = self.abc_file.method_bodies[ixMB]
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)method_body={BM.DumpVar(method_body)}')
        environment = self.create_method_environment(method_body, *args)
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)environment={BM.DumpVar(environment)}')
        res =self.execute_code(method_body.code, environment)
        return res
    def call_ClassClassInit(self, index_or_name: Union[ABCMethodIndex, str], *args) -> Any:
        """
        Call the specified class class initialise method. Done once only
        """
        print(f'## @{BM.LINE()} ## call_static ## ...')
        if isinstance(index_or_name, int):
            index = ABCMethodIndex(index_or_name)
        elif isinstance(index_or_name, str):
            index = self.lookup_method(index_or_name)
        else:
            raise ValueError(index_or_name)
        methodInfo = self.abc_file.methods[index]
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)index_or_name={BM.DumpVar(index_or_name)} -> index {BM.DumpVar(index)} mi.n={methodInfo.nam_name}:{"(add methodInfo)"} #M2B={len(self.method_to_body)} #a.MB={len(self.abc_file.method_bodies)}')

        # TODO: init script on demand.
        ixMB = self.method_to_body[index]
        method_body = self.abc_file.method_bodies[ixMB]
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)method_body={BM.DumpVar(method_body)}')
        environment = self.create_method_environment(method_body, *args)
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)environment={BM.DumpVar(environment)}')
        res =self.execute_code(method_body.code, environment)
        return res

    def call_static(self, index_or_name: Union[ABCMethodIndex, str], *args) -> Any:
        """
        Call the specified static method and get a return value.
        """
        print(f'## @{BM.LINE()} ## call_static ## ...')
        if isinstance(index_or_name, int):
            index = ABCMethodIndex(index_or_name)
        elif isinstance(index_or_name, str):
            index = self.lookup_method(index_or_name)
        else:
            raise ValueError(index_or_name)
        methodInfo = self.abc_file.methods[index]
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)index_or_name={BM.DumpVar(index_or_name)} -> index {BM.DumpVar(index)} mi.n={methodInfo.nam_name}:{"(add methodInfo)"} #M2B={len(self.method_to_body)} #a.MB={len(self.abc_file.method_bodies)}')

        # TODO: init script on demand.
        ixMB = self.method_to_body[index]
        method_body = self.abc_file.method_bodies[ixMB]
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)method_body={BM.DumpVar(method_body)}')
        environment = self.create_method_environment(method_body, *args)
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)environment={BM.DumpVar(environment)}')
        res =self.execute_code(method_body.code, environment)
        return res

    def call_method(self, index_or_name: Union[ABCMethodIndex, str], this: Any, *args) -> Any:
        """
        Call the specified method and get a return value.
        """
        print(f'## @{BM.LINE()} ## call_method ## ...')
        if isinstance(index_or_name, int):
            index = ABCMethodIndex(index_or_name)
        elif isinstance(index_or_name, str):
            index = self.lookup_method(index_or_name)
        else:
            raise ValueError(index_or_name)
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)index_or_name={BM.DumpVar(index_or_name)} > index {BM.DumpVar(index)}')

        # TODO: init script on demand.
        method_body = self.abc_file.method_bodies[self.method_to_body[index]]
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)method_body={BM.DumpVar(method_body)}')
        environment = self.create_method_environment(method_body, this, *args)
        if self.cbOnInsExe is not None: self.cbOnInsExe.MakeExtraObservation(f'(v.p)environment={BM.DumpVar(environment)}')
        return self.execute_code(method_body.code, environment)

    def execute_code(self, code: memoryview, environment: MethodEnvironment) -> Any:
        """
        Execute the byte-code and get a return value.
        """
        reader = MemoryViewReader(code)
        while True:
            try:
                # FIXME: cache already read instructions.
                offsetOfInst = reader.position
                avm2.abc.instructions.read_instruction(reader).doExecute(self, environment, offsetOfInst)
            except ASReturnException as e:
                return e.return_value
            except ASJumpException as e:
                reader.position += e.offset

    # Unclassified.
    # ------------------------------------------------------------------------------------------------------------------

    def create_method_environment(self, method_body: ASMethodBody, this: Any, *args) -> MethodEnvironment:
        """
        Create method execution environment: registers and stacks.
        """
        method = self.abc_file.methods[method_body.method_ix]
        # There are `method_body_info.local_count` registers.
        # registers: List[Any] = [undefined] * method_body.local_count
        registers: List[Any] = list() # [-1] = undefined2 # DEBUG aid in checking ASObject definitions
        for _ in range(method_body.local_count):
          registers.append(ASUndefined(BM.LINE(False)))
        # Register 0 holds the "this" object. This value is never null.
        registers[0] = this # Register 0 holds the “this” object. This value is never null .
        # Registers 1 through `method_info.param_count` holds parameter values coerced to the declared types
        # of the parameters.
        assert len(args) <= method.param_count
        registers[1:len(args) + 1] = args
        # If fewer than `method_body_info.local_count` values are supplied to the call then the remaining values are
        # either the values provided by default value declarations (optional arguments) or the value `undefined`.
        if method.options:
            assert len(method.options) <= method.param_count
            for i, option in zip(range(len(args) + 1, method_body.local_count), method.options):
                registers[i] = self.get_constant(option.kind, option.value)
        # If `NEED_REST` is set in `method_info.flags`, the `method_info.param_count + 1` register is set up to
        # reference an array that holds the superflous arguments.
        if MethodFlags.NEED_REST in method.flags:
            registers[method.param_count + 1] = args[method.param_count:]
        # If `NEED_ARGUMENTS` is set in `method_info.flags`, the `method_info.param_count + 1` register is set up
        # to reference an "arguments" object that holds all the actual arguments: see ECMA-262 for more
        # information.
        if MethodFlags.NEED_ARGUMENTS in method.flags:
            registers[method.param_count + 1] = args
        assert len(registers) == method_body.local_count
        # FIXME: unsure about the global object here.
        return MethodEnvironment(registers=registers, scope_stack=[self.global_object])

    def get_constant(self, kind: ConstantKind, index: int) -> Any:
        """
        Get constant specified by its kind and index.
        """
        if kind == ConstantKind.TRUE:
            return True
        if kind == ConstantKind.FALSE:
            return False
        if kind == ConstantKind.NULL:
            return None
        if kind == ConstantKind.UNDEFINED:
            return undefined
        if kind == ConstantKind.INT:
            return self.integers[index]
        if kind == ConstantKind.NAMESPACE:
            return self.namespaces[index]
        if kind == ConstantKind.MULTINAME:
            return self.multinames[index]
        raise NotImplementedError(kind)


@dataclass
class MethodEnvironment:
    registers: List[Any]  # FIXME: should be ASObject's too.
    scope_stack: List[ASObject]
    operand_stack: List[Any] = field(default_factory=list)  # FIXME: should be ASObject's too.
    lastNInstr: List(str) = field(default_factory=list)
    instrExeCnt: int = 0


def execute_tag(tag: Tag) -> VirtualMachine:
    """
    Parse and execute DO_ABC tag.
    """
    assert tag.type_ == TagType.DO_ABC
    doAbcTag = DoABCTag(tag.raw)
    res = execute_do_abc_tag(doAbcTag)
    return res


def execute_do_abc_tag(do_abc_tag: DoABCTag) -> VirtualMachine:
    """
    Create a virtual machine and execute the tag.
    """
    abcFile = ABCFile(MemoryViewReader(do_abc_tag.abc_file))
    vm = VirtualMachine(abcFile)
    return vm
