from __future__ import annotations

from dataclasses import dataclass, fields
import sys
from typing import Any, Callable, ClassVar, Dict, Tuple, Type, TypeVar, NewType, Optional

import BrewMaths as BM

import avm2.vm
from avm2.exceptions import ASReturnException, ASJumpException
from avm2.runtime import undefined
from avm2.abc.parser import read_array
from avm2.io import MemoryViewReader
from avm2.abc.enums import MultinameKind

import inspect

def read_instruction(reader: MemoryViewReader) -> Instruction:
    opcode: int = reader.read_u8()
    # noinspection PyCallingNonCallable
    return opcode_to_instruction[opcode](opcode, reader)


u8 = NewType('u8', int)
u30 = NewType('u30', int)
uint = NewType('uint', int)
s24 = NewType('s24', int)

@dataclass
class Instruction:
    maxlastNInstr = 5 # maximum number of previous instructions to track
    readers: ClassVar[Dict[str, Callable[[MemoryViewReader], Any]]] = {
        u8.__name__: MemoryViewReader.read_u8,
        u30.__name__: MemoryViewReader.read_int,
        uint.__name__: MemoryViewReader.read_u32,
        s24.__name__: MemoryViewReader.read_s24,
    }

    # add some way to track things
    def tallyProgress(theInstance: Instruction, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment, offsetOfInstruction: int):
        environment.instrExeCnt += 1
        environment.lastNInstr.append(f'+{hex(offsetOfInstruction)} S#{len(environment.scope_stack)}, O#{len(environment.operand_stack)}, I={type(theInstance).__name__}')
        if len(environment.lastNInstr) > Instruction.maxlastNInstr:
          del environment.lastNInstr[0]

        # any callback?
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.ObserveInstructionExecuting(theInstance, machine, environment, offsetOfInstruction)

    opcode: int

    def __init__(self, opcode: int, reader: MemoryViewReader):
        self.opcode = opcode
        for field in fields(self):
            if field.name == 'opcode': continue
            setattr(self, field.name, self.readers[field.type](reader))

    def doExecute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment, offsetOfInstruction: int) -> Optional[int]:
        self.tallyProgress(machine, environment, offsetOfInstruction)
        return self.execute(machine, environment)

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment) -> Optional[int]:
        raise NotImplementedError(self)

class CallbackOnInstructionExecuting:
  """
  Derive your callback listener from here
  """
  def ObserveInstructionExecuting(self, theInstruction: Instruction, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment, offsetOfInstruction: int):
    raise NotImplementedError(F'Someone forgot to derive their listener from here ({self})')
  def MakeExtraObservation(self, extraObservation):
    pass

T = TypeVar('T', bound=Instruction)
opcode_to_instruction: Dict[int, Type[T]] = {}

@dataclass
class CallbackOnInstructionExecuting_GenerateAVM2InstructionTrace(CallbackOnInstructionExecuting):
  """
  set limitCalls to -1 for all, or 0+ to limit the number of calls processed
  """
  limitCalls: int

  def ObserveInstructionExecuting(self, theInstruction: Instruction, machine: VirtualMachine, environment: MethodEnvironment, offsetOfInstruction: int):
    self.callsSoFar += 1

    if self.callsSoFar == 1 and self.callsSoFar < self.limitCalls: # display on first call
      DumpEnvironmentRegisters(machine, environment)

    if self.limitCalls >= 0 and self.callsSoFar < self.limitCalls:
      print(f'\t{BM.LINE()}: {theInstruction}\t\t// +{hex(offsetOfInstruction)} #{self.callsSoFar}')

  def MakeExtraObservation(self, extraObservation):
    if self.limitCalls >= 0 and self.callsSoFar < self.limitCalls:
      print(f'\t{BM.LINE()}: \tExtra:{extraObservation}.')

  def __init__(self, limitCalls: int):
    self.limitCalls = limitCalls
    self.callsSoFar: int = 0


def instruction(opcode: int) -> Callable[[], Type[T]]:
    def wrapper(class_: Type[T]) -> Type[T]:
        assert opcode not in opcode_to_instruction, opcode_to_instruction[opcode]
        opcode_to_instruction[opcode] = class_
        return dataclass(init=False)(class_)
    return wrapper


# Instructions implementation.
# ----------------------------------------------------------------------------------------------------------------------

@instruction(160)
class Add(Instruction): # …, value1, value2 => …, value3
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        result = value_1 + value_2
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
        environment.operand_stack.append(result)

@instruction(197)
class AddInteger(Instruction): # …, value1, value2 => …, value3
    """
    Pop value1 and value2 off of the stack and convert them to int values using the ToInt32
    algorithm (ECMA-262 section 9.5). Add the two int values and push the result onto the
    stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        result = int(value_1) + int(value_2)
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
        environment.operand_stack.append(result)


@instruction(134)
class AsType(Instruction):
    index: u30


@instruction(135)
class AsTypeLate(Instruction):
    pass


@instruction(168)
class BitAnd(Instruction):
    pass


@instruction(151)
class BitNot(Instruction):
    pass


@instruction(169)
class BitOr(Instruction):
    pass


@instruction(170)
class BitXor(Instruction):
    pass


@instruction(65)
class Call(Instruction): # …, function, receiver, arg1, arg2, ..., argn => …, value
    arg_count: u30


@instruction(67)
class CallMethod(Instruction): # …, receiver, arg1, arg2, ..., argn => …, value
    index: u30
    arg_count: u30


@instruction(70)
class CallProperty(Instruction): # …, obj, [ns], [name], arg1,...,argn => …, value
    index: u30
    arg_count: u30


@instruction(76)
class CallPropLex(Instruction): # …, obj, [ns], [name], arg1,...,argn => …, value
    index: u30
    arg_count: u30


@instruction(79)
class CallPropVoid(Instruction): # …, obj, [ns], [name], arg1,...,argn => …
    index: u30
    arg_count: u30


@instruction(68)
class CallStatic(Instruction): # …, receiver, arg1, arg2, ..., argn => …, value
    index: u30
    arg_count: u30


@instruction(69)
class CallSuper(Instruction):
    index: u30
    arg_count: u30


@instruction(78)
class CallSuperVoid(Instruction):
    index: u30
    arg_count: u30


@instruction(120)
class CheckFilter(Instruction):
    pass


@instruction(128)
class Coerce(Instruction):
    index: u30


@instruction(130)
class CoerceAny(Instruction):
    pass


@instruction(133)
class CoerceString(Instruction):
    pass


@instruction(66)
class Construct(Instruction): # …, object, arg1, arg2, ..., argn => …, value
    """
    arg_count is a u30 that is the number of arguments present on the stack. object is the
    function that is being constructed. This will invoke the [[Construct]] property on object with
    the given arguments. The new instance generated by invoking [[Construct]] will be pushed
    onto the stack.
    """
    arg_count: u30

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
      print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}.{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_code.co_firstlineno}. BTW a#={self.arg_count}', file=sys.stderr)
      # TODO add proper code
      argN=[]
      for ix in range(self.arg_count)[::-1]:
        theArg = environment.operand_stack.pop()
        print(f'arg[{ix}]={theArg}')
        argN.insert(0, theArg)

      theObj = environment.operand_stack.pop()

      theValue = '#TODO#'
      environment.operand_stack.append(theValue)


@instruction(74)
class ConstructProp(Instruction): # …, obj, [ns], [name], arg1,...,argn => …, value
    """
    arg_count is a u30 that is the number of arguments present on the stack. The number of
    arguments specified by arg_count are popped off the stack and saved.

    index is a u30 that must be an index into the multiname constant pool. If the multiname at
    that index is a runtime multiname the name and/or namespace will also appear on the stack
    so that the multiname can be constructed correctly at runtime.

    obj is the object to resolve the multiname in.

    The property specified by the multiname at index is resolved on the object obj. The
    [[Construct]] property is invoked on the value of the resolved property with the arguments
    obj, arg1, ..., argn. The new instance generated by invoking [[Construct]] will be pushed
    onto the stack.
    """
    index: u30
    arg_count: u30

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
      print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}.{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_code.co_firstlineno}. BTW i={self.index}, a#={self.arg_count}', file=sys.stderr)
      # TODO add proper code
      argN=[]
      for ix in range(self.arg_count)[::-1]:
        theArg = environment.operand_stack.pop()
        print(f'arg[{ix}]={theArg}')
        argN.insert(0, theArg)

      # TODO is it a runtime multiname?
      # cf FindPropStrict for some ideas

      isMultinameRuntimeName = False # Add code to determine Name
      isMultinameRuntimeNS = False # Add code to determine Namespace

      if isMultinameRuntimeName:
        theName = environment.operand_stack.pop()

      if isMultinameRuntimeNS:
        theNS = environment.operand_stack.pop()

      theObj = environment.operand_stack.pop()

      theValue = '#TODO#'
      environment.operand_stack.append(theValue)


@instruction(73)
class ConstructSuper(Instruction): # …, object, arg1, arg2, ..., argn => …
    """
    arg_count is a u30 that is the number of arguments present on the stack. This will invoke the
    constructor on the base class of object with the given arguments.
    """
    arg_count: u30

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
      print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}.{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_code.co_firstlineno}', file=sys.stderr)
      # TODO add proper code
      #print(f'a#={self.arg_count}')
      argN=[]
      for ix in range(self.arg_count)[::-1]:
        theArg = environment.operand_stack.pop()
        print(f'arg[{ix}]={theArg}')
        argN.insert(0, theArg)

      theObj = environment.operand_stack.pop()

      # TODO Do something with theObj


@instruction(118)
class ConvertToBoolean(Instruction):
    pass


@instruction(115)
class ConvertToInteger(Instruction): # …, value => …, intvalue
    """
    `value` is popped off of the stack and converted to an integer. The result, `intvalue`, is pushed
    onto the stack. This uses the `ToInt32` algorithm, as described in ECMA-262 section 9.5, to
    perform the conversion.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = int(environment.operand_stack.pop())
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.operand_stack.append(value)


@instruction(117)
class ConvertToDouble(Instruction): # …, value => …, doublevalue
    """
    `value` is popped off of the stack and converted to a double. The result, `doublevalue`, is pushed
    onto the stack. This uses the `ToNumber` algorithm, as described in ECMA-262 section 9.3,
    to perform the conversion.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = float(environment.operand_stack.pop())
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.operand_stack.append(value)


@instruction(119)
class ConvertToObject(Instruction):
    pass


@instruction(116)
class ConvertToUnsignedInteger(Instruction):
    pass


@instruction(112)
class ConvertToString(Instruction):
    pass


@instruction(239)
class Debug(Instruction):
    debug_type: u8
    index: u30
    reg: u8
    extra: u30


@instruction(241)
class DebugFile(Instruction):
    index: u30


@instruction(240)
class DebugLine(Instruction):
    linenum: u30


@instruction(148)
class DecLocal(Instruction):
    index: u30


@instruction(195)
class DecLocalInteger(Instruction):
    index: u30


@instruction(147)
class Decrement(Instruction):
    pass


@instruction(193)
class DecrementInteger(Instruction):
    pass


@instruction(106)
class DeleteProperty(Instruction):
    index: u30


@instruction(163)
class Divide(Instruction): # …, value1, value2 => …, value3
    """
    Pop `value1` and `value2` off of the stack, convert `value1` and `value2` to `Number` to create
    `value1_number` and `value2_number`. Divide `value1_number` by `value2_number` and push the
    result onto the stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        result = value_1 / value_2
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
        environment.operand_stack.append(result)


@instruction(42)
class Dup(Instruction): # …, value => …, value, value
    """
    Duplicates the top value of the stack, and then pushes the duplicated value onto the stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.operand_stack.extend([value, value])


@instruction(6)
class DXNS(Instruction):
    index: u30


@instruction(7)
class DXNSLate(Instruction):
    pass


@instruction(171)
class EqualsOperation(Instruction):
    pass


@instruction(114)
class EscXAttr(Instruction):
    pass


@instruction(113)
class EscXElem(Instruction):
    pass


@instruction(94)
class FindProperty(Instruction): # …, [ns], [name] => …, obj
    """
    index is a u30 that must be an index into the multiname constant pool. If the multiname at
    that index is a runtime multiname the name and/or namespace will also appear on the stack
    so that the multiname can be constructed correctly at runtime.

    This searches the scope stack, and then the saved scope in the current method closure, for a
    property with the name specified by the multiname at index.

    If any of the objects searched is a with scope, its declared and dynamic properties will be
    searched for a match. Otherwise only the declared traits of a scope will be searched. The
    global object will have its declared traits, dynamic properties, and prototype chain searched.

    If the property is resolved then the object it was resolved in is pushed onto the stack. If the
    property is unresolved in all objects on the scope stack then the global object is pushed onto
    the stack.
    """
    index: u30
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
      print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}.{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_code.co_firstlineno}. BTW i={self.index}', file=sys.stderr)

      # TODO add proper code

      # TODO is it a runtime multiname?
      # cf FindPropStrict for some ideas

      isMultinameRuntimeName = False # Add code to determine Name
      isMultinameRuntimeNS = False # Add code to determine Namespace

      if isMultinameRuntimeName:
        theName = environment.operand_stack.pop()


      if isMultinameRuntimeNS:
        theNS = environment.operand_stack.pop()

      theValue = '#TODO# cf FindPropStrict'
      environment.operand_stack.append(theValue)


@instruction(93)
class FindPropStrict(Instruction): # …, [ns], [name] => …, obj
    """
    `index` is a `u30` that must be an index into the `multiname` constant pool. If the multiname at
    that index is a runtime multiname the name and/or namespace will also appear on the stack
    so that the multiname can be constructed correctly at runtime.

    This searches the scope stack, and then the saved scope in the method closure, for a property
    with the name specified by the multiname at `index`.

    If any of the objects searched is a `with` scope, its declared and dynamic properties will be
    searched for a match. Otherwise only the declared traits of a scope will be searched. The
    global object will have its declared traits, dynamic properties, and prototype chain searched.

    If the property is resolved then the object it was resolved in is pushed onto the stack. If the
    property is unresolved in all objects on the scope stack then an exception is thrown.

    A `ReferenceError` is thrown if the property is not resolved in any object on the scope stack.
    """

    index: u30

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}. BTW i={self.index}', file=sys.stderr)
        multiname = machine.multinames[self.index]
        # TODO: other kinds of multinames.
        assert multiname.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A), multiname
        try:

            theStack      = environment.scope_stack
            theName       = machine.strings[multiname.nam_ix]
            theNamespaces = [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]]
            if machine.callbackOnInstructionExecuting is not None:
              machine.callbackOnInstructionExecuting.MakeExtraObservation(f'tS#{len(theStack)}={BM.DumpVar(theStack)}')
              machine.callbackOnInstructionExecuting.MakeExtraObservation(f'tN={BM.DumpVar(theName)}')
              machine.callbackOnInstructionExecuting.MakeExtraObservation(f'tNa={BM.DumpVar(theNamespaces)}')
            object_, name, namespace = machine.resolve_multiname(
                theStack, # environment.scope_stack,
                theName, # machine.strings[multiname.nam_ix],
                theNamespaces # [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]],
            )
            # object_, _, _ = machine.resolve_multiname(
                # environment.scope_stack,
                # machine.strings[multiname.nam_ix],
                # [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]],
            # )
        except KeyError:
            raise NotImplementedError('ReferenceError')
        else:
            environment.operand_stack.append(object_)


@instruction(89)
class GetDescendants(Instruction):
    index: u30


@instruction(100)
class GetGlobalScope(Instruction):
    pass


@instruction(110)
class GetGlobalSlot(Instruction):
    slot_ix: u30


@instruction(96)
class GetLex(Instruction): # … => …, obj
    """
    `index` is a `u30` that must be an index into the multiname constant pool. The multiname at
    `index` must not be a runtime multiname, so there are never any optional namespace or name
    values on the stack.

    This is the equivalent of doing a `findpropstrict` followed by a `getproperty`. It will find the
    object on the scope stack that contains the property, and then will get the value from that
    object. See "Resolving multinames" on page 10.

    A `ReferenceError` is thrown if the property is unresolved in all of the objects on the scope
    stack.
    """

    index: u30

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        multiname = machine.multinames[self.index]
        assert multiname.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A)
        try:
            theStack      = environment.scope_stack
            theName       = machine.strings[multiname.nam_ix]
            theNamespaces = [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]]
            if machine.callbackOnInstructionExecuting is not None:
              machine.callbackOnInstructionExecuting.MakeExtraObservation(f'tS#{len(theStack)}={BM.DumpVar(theStack)}')
              machine.callbackOnInstructionExecuting.MakeExtraObservation(f'tN={BM.DumpVar(theName)}')
              machine.callbackOnInstructionExecuting.MakeExtraObservation(f'tNa={BM.DumpVar(theNamespaces)}')
            object_, name, namespace = machine.resolve_multiname(
                theStack, # environment.scope_stack,
                theName, # machine.strings[multiname.nam_ix],
                theNamespaces, # [machine.strings[machine.namespaces[multiname.ns_ix].nam_ix]],
            )
        except KeyError:
            raise NotImplementedError('ReferenceError')
        else:
            environment.operand_stack.append(object_.properties[namespace, name])


@instruction(98)
class GetLocal(Instruction):
    index: u30

def DumpEnvironmentRegisters(machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
  if machine.callbackOnInstructionExecuting is not None:
    if len(environment.registers) > 0:
      machine.callbackOnInstructionExecuting.MakeExtraObservation(f'BTW ER0={BM.DumpVar(environment.registers[0])}')
    if len(environment.registers) > 1:
      machine.callbackOnInstructionExecuting.MakeExtraObservation(f'BTW ER1={BM.DumpVar(environment.registers[1])}')
    if len(environment.registers) > 2:
      machine.callbackOnInstructionExecuting.MakeExtraObservation(f'BTW ER2={BM.DumpVar(environment.registers[2])}')
    if len(environment.registers) > 3:
      machine.callbackOnInstructionExecuting.MakeExtraObservation(f'BTW ER3={BM.DumpVar(environment.registers[3])}')

@instruction(208)
class GetLocal0(Instruction): # … => …, value
    """
    `<n>` is the index of a local register. The value of that register is pushed onto the stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.registers[0]
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        # if machine.callbackOnInstructionExecuting is not None: DumpEnvironmentRegisters(machine, environment)
        environment.operand_stack.append(value)


@instruction(209)
class GetLocal1(Instruction): # … => …, value
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.registers[1]
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        # if machine.callbackOnInstructionExecuting is not None: DumpEnvironmentRegisters(machine, environment)
        environment.operand_stack.append(value)


@instruction(210)
class GetLocal2(Instruction): # … => …, value
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.registers[2]
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        # if machine.callbackOnInstructionExecuting is not None: DumpEnvironmentRegisters(machine, environment)
        environment.operand_stack.append(value)


@instruction(211)
class GetLocal3(Instruction): # … => …, value
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.registers[3]
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        # if machine.callbackOnInstructionExecuting is not None: DumpEnvironmentRegisters(machine, environment)
        environment.operand_stack.append(value)


@instruction(102)
class GetProperty(Instruction):
    index: u30


@instruction(101)
class GetScopeObject(Instruction): # … => …, scope
    """
    `index` is an unsigned byte that specifies the index of the scope object to retrieve from the local
    scope stack. `index` must be less than the current depth of the scope stack. The scope at that
    `index` is retrieved and pushed onto the stack. The scope at the top of the stack is at index
    `scope_depth - 1`, and the scope at the bottom of the stack is index `0`.
    """

    index: u8

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.scope_stack[self.index]
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.operand_stack.append(value)


@instruction(108)
class GetSlot(Instruction):
    slot_ix: u30


@instruction(4)
class GetSuper(Instruction):
    index: u30


@instruction(176)
class GreaterEquals(Instruction): # …, value1, value2 => …, result
    """
    Pop `value1` and `value2` off of the stack. Compute `value1 < value2` using the Abstract
    Relational Comparison Algorithm, as described in ECMA-262 section 11.8.5. If the result of
    the comparison is `false`, push `true` onto the stack. Otherwise push `false` onto the stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        result = value_1 >= value_2
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
        environment.operand_stack.append(result)


@instruction(175)
class GreaterThan(Instruction):
    pass


@instruction(31)
class HasNext(Instruction):
    pass


@instruction(50)
class HasNext2(Instruction):
    object_reg: uint
    index_reg: uint


@instruction(19)
class IfEq(Instruction):
    offset: s24


@instruction(18)
class IfFalse(Instruction): # …, value => …
    """
    Pop value off the stack and convert it to a `Boolean`. If the converted value is `false`, jump the
    number of bytes indicated by `offset`. Otherwise continue executing code from this point.
    """

    offset: s24

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        if not environment.operand_stack.pop():
            if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'jump {self.offset}>')
            raise ASJumpException(self.offset)


@instruction(24)
class IfGE(Instruction):
    offset: s24


@instruction(23)
class IfGT(Instruction):
    offset: s24


@instruction(22)
class IfLE(Instruction):
    offset: s24


@instruction(21)
class IfLT(Instruction): # …, value1, value2 => …
    """
    `offset` is an `s24` that is the number of bytes to jump if `value1` is less than `value2`.

    Compute value1 < value2 using the abstract relational comparison algorithm in ECMA-262
    section 11.8.5. If the result of the comparison is `true`, jump the number of bytes indicated
    by `offset`. Otherwise continue executing code from this point.
    """

    offset: s24

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        if value_1 < value_2:
            if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'jump {self.offset}>')
            raise ASJumpException(self.offset)


@instruction(15)
class IfNGE(Instruction):
    offset: s24


@instruction(14)
class IfNGT(Instruction): # …, value1, value2 => …
    """
    Compute `value2 < value1` using the abstract relational comparison algorithm in ECMA-262
    section 11.8.5. If the result of the comparison is not `true`, jump the number of bytes
    indicated by `offset`. Otherwise continue executing code from this point.
    """

    offset: s24

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        # FIXME: NaN.
        if not value_1 > value_2:
            if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'jump {self.offset}>')
            raise ASJumpException(self.offset)


@instruction(13)
class IfNLE(Instruction):
    offset: s24


@instruction(12)
class IfNLT(Instruction): # …, value1, value2 => …
    """
    Compute `value1 < value2` using the abstract relational comparison algorithm in ECMA-262
    section 11.8.5. If the result of the comparison is false, then jump the number of bytes
    indicated by `offset`. Otherwise continue executing code from this point.

    This appears to have the same effect as `ifge`, however, their handling of `NaN` is different. If
    either of the compared values is `NaN` then the comparison `value1 < value2` will return
    `undefined`. In that case `ifnlt` will branch (`undefined` is not true), but `ifge` will not
    branch.
    """

    offset: s24

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        # FIXME: NaN.
        if not value_1 < value_2:
            if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'jump {self.offset}>')
            raise ASJumpException(self.offset)


@instruction(20)
class IfNE(Instruction):
    """
    Compute `value1 == value2` using the abstract relational comparison algorithm in ECMA-262
    section 11.8.5. If the result of the comparison is false, then jump the number of bytes
    indicated by `offset`. Otherwise continue executing code from this point.
    """

    offset: s24

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        # FIXME: NaN. maybe
        if not value_1 == value_2:
            if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'jump {self.offset}>')
            raise ASJumpException(self.offset)


@instruction(25)
class IfStrictEq(Instruction):
    offset: s24


@instruction(26)
class IfStrictNE(Instruction):
    offset: s24


@instruction(17)
class IfTrue(Instruction):
    offset: s24


@instruction(180)
class In(Instruction):
    pass


@instruction(146)
class IncLocal(Instruction):
    index: u30


@instruction(194)
class IncLocalInteger(Instruction):
    index: u30


@instruction(145)
class Increment(Instruction):
    pass


@instruction(192)
class IncrementInteger(Instruction):
    pass


@instruction(104)
class InitProperty(Instruction):
    index: u30


@instruction(177)
class InstanceOf(Instruction):
    pass


@instruction(178)
class IsType(Instruction):
    index: u30


@instruction(179)
class IsTypeLate(Instruction):
    pass


@instruction(16)
class Jump(Instruction):
    offset: s24
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
      if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'jump {self.offset}>')
      raise ASJumpException(self.offset)


@instruction(8)
class Kill(Instruction):
    index: u30


@instruction(9)
class Label(Instruction):
    pass


@instruction(174)
class LessEquals(Instruction):
    pass


@instruction(173)
class LessThan(Instruction):
    pass


@instruction(27)
class LookupSwitch(Instruction): # …, index => …
    default_offset: s24
    case_offsets: Tuple[s24, ...]

    # noinspection PyMissingConstructor
    def __init__(self, reader: MemoryViewReader):
        self.default_offset = reader.read_s24()
        case_count = reader.read_int()
        self.case_offsets = read_array(reader, MemoryViewReader.read_s24, case_count + 1)


@instruction(165)
class LeftShift(Instruction):
    pass


@instruction(164)
class Modulo(Instruction):
    pass


@instruction(162)
class Multiply(Instruction):
    pass


@instruction(199)
class MultiplyInteger(Instruction):
    pass


@instruction(144)
class Negate(Instruction):
    pass


@instruction(196)
class NegateInteger(Instruction):
    pass


@instruction(87)
class NewActivation(Instruction):
    pass


@instruction(86)
class NewArray(Instruction):
    arg_count: u30


@instruction(90)
class NewCatch(Instruction):
    index: u30


@instruction(88)
class NewClass(Instruction):
    index: u30


@instruction(64)
class NewFunction(Instruction):
    index: u30


@instruction(85)
class NewObject(Instruction):
    arg_count: u30


@instruction(30)
class NextName(Instruction):
    pass


@instruction(35)
class NextValue(Instruction):
    pass


@instruction(2)
class Nop(Instruction):
    pass


@instruction(150)
class Not(Instruction):
    pass


@instruction(41)
class Pop(Instruction): # …, value => …
    """
    Pops the top value from the stack and discards it.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'popped=<{BM.DumpVar(value)}>')


@instruction(29)
class PopScope(Instruction):
    pass


@instruction(36)
class PushByte(Instruction): # … => …, value
    byte_value: u8

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = self.byte_value
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.operand_stack.append(value)


@instruction(47)
class PushDouble(Instruction): # … => …, value
    """
    `index` is a `u30` that must be an index into the `double` constant pool. The double value at
    `index` in the `double` constant pool is pushed onto the stack.
    """

    index: u30

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = machine.doubles[self.index]
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.operand_stack.append(value)


@instruction(39)
class PushFalse(Instruction): # … => …, false
    """
    Push the false value onto the stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        environment.operand_stack.append(False)


@instruction(45)
class PushInteger(Instruction): # … => …, value
    """
    `index` is a `u30` that must be an index into the `integer` constant pool. The int value at `index` in
    the integer constant pool is pushed onto the stack.
    """

    index: u30

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = machine.integers[self.index]
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.operand_stack.append(value)


@instruction(49)
class PushNamespace(Instruction):
    index: u30


@instruction(40)
class PushNaN(Instruction):
    pass


@instruction(32)
class PushNull(Instruction):
    """
    Push the `null` value onto the stack. Maybe use 'None' ?
    """
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        environment.operand_stack.append(None)


@instruction(48)
class PushScope(Instruction): # …, value => …
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        assert value is not None and value is not undefined
        environment.scope_stack.append(value)


@instruction(37)
class PushShort(Instruction):
    value: u30


@instruction(44)
class PushString(Instruction):
    index: u30


@instruction(38)
class PushTrue(Instruction): # … => …, true
    """
    Push the `true` value onto the stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        environment.operand_stack.append(True)


@instruction(46)
class PushUnsignedInteger(Instruction):
    index: u30


@instruction(33)
class PushUndefined(Instruction):
    pass


@instruction(28)
class PushWith(Instruction):
    pass


@instruction(72)
class ReturnValue(Instruction): # …, return_value => …
    """
    Return from the currently executing method. This returns the top value on the stack.
    `return_value` is popped off of the stack, and coerced to the expected return type of the
    method. The coerced value is what is actually returned from the method.

    A `TypeError` is thrown if `return_value` cannot be coerced to the expected return type of the
    executing method.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        # FIXME: coerce to the expected return type.
        value = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        raise ASReturnException(value)


@instruction(71)
class ReturnVoid(Instruction): # … => …
    """
    Return from the currently executing method. This returns the value `undefined`. If the
    method has a return type, then undefined is coerced to that type and then returned.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        raise ASReturnException(undefined)


@instruction(166)
class RightShift(Instruction):
    pass


@instruction(99)
class SetLocal(Instruction):
    index: u30


@instruction(212)
class SetLocal0(Instruction): # …, value => …
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.registers[0] = value


@instruction(213)
class SetLocal1(Instruction): # …, value => …
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.registers[1] = value


@instruction(214)
class SetLocal2(Instruction): # …, value => …
    """
    `<n>` is an index of a local register. The register at that index is set to value, and value is
    popped off the stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.registers[2] = value


@instruction(215)
class SetLocal3(Instruction): # …, value => …
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'value=<{BM.DumpVar(value)}>')
        environment.registers[3] = value


@instruction(111)
class SetGlobalSlot(Instruction):
    slot_ix: u30


@instruction(97)
class SetProperty(Instruction): # …, obj, [ns], [name], value => …
    """
    value is the value that the property will be set to. value is popped off the stack and saved.

    index is a u30 that must be an index into the multiname constant pool. If the multiname at
    that index is a runtime multiname the name and/or namespace will also appear on the stack
    so that the multiname can be constructed correctly at runtime.

    The property with the name specified by the multiname will be resolved in obj, and will be
    set to value. If the property is not found in obj, and obj is dynamic then the property will be
    created and set to value. See “Resolving multinames” on page 10

    [Adobe ActionScript Virtual Machine 2 (AVM2)].
    """
    index: u30
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
      print(f'@{BM.LINE()} !!If you see this, you need to properly implement {type(self).__name__}.{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_code.co_firstlineno}. BTW i={self.index}', file=sys.stderr)

      # TODO is it a runtime multiname?
      # cf FindPropStrict for some ideas

      isMultinameRuntimeName = False # Add code to determine Name
      isMultinameRuntimeNS = False # Add code to determine Namespace

      if isMultinameRuntimeName:
        theName = environment.operand_stack.pop()

      if isMultinameRuntimeNS:
        theNS = environment.operand_stack.pop()

      theObj = environment.operand_stack.pop()
      # TODO set theObj property to value


@instruction(109)
class SetSlot(Instruction):
    slot_ix: u30


@instruction(5)
class SetSuper(Instruction):
    index: u30


@instruction(172)
class StrictEquals(Instruction):
    pass


@instruction(161)
class Subtract(Instruction):
    pass


@instruction(198)
class SubtractInteger(Instruction): # …, value1, value2 => …, value3
    """
    Pop `value1` and `value2` off of the stack and convert `value1` and `value2` to int to create
    `value1_int` and `value2_int`. Subtract `value2_int` from `value1_int`. Push the result onto the
    stack.
    """

    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        result = int(value_1) - int(value_2)
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'result=<{BM.DumpVar(result)}>')
        environment.operand_stack.append(result)


@instruction(43)
class Swap(Instruction): # …, value1, value2 => …, value2, value1
    """
    Swap the top two values on the stack. Pop value2 and value1. Push value2, then push value1.
    """
    def execute(self, machine: avm2.vm.VirtualMachine, environment: avm2.vm.MethodEnvironment):
        value_2 = environment.operand_stack.pop()
        value_1 = environment.operand_stack.pop()
        if machine.callbackOnInstructionExecuting is not None: machine.callbackOnInstructionExecuting.MakeExtraObservation(f'{BM.DumpVar(value_1)} <=> <{BM.DumpVar(value_2)}>')
        environment.operand_stack.append(value_2)
        environment.operand_stack.append(value_1)


@instruction(3)
class Throw(Instruction):
    pass


@instruction(149)
class TypeOf(Instruction):
    pass


@instruction(167)
class UnsignedRightShift(Instruction):
    pass
