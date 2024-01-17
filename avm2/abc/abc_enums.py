from enum import IntEnum, IntFlag


class NamespaceKind(IntEnum):
    NAMESPACE = 0x08
    PACKAGE_NAMESPACE = 0x16
    PACKAGE_INTERNAL_NS = 0x17
    PROTECTED_NAMESPACE = 0x18
    EXPLICIT_NAMESPACE = 0x19
    STATIC_PROTECTED_NS = 0x1A
    PRIVATE_NS = 0x05


class MultinameKind(IntEnum):
    Q_NAME = 0x07       # simple FQ name. nam_ix is an index into the string constant pool, and the ns_ix is an index into the namespace constant pool.
    Q_NAME_A = 0x0D     # simple FQ name. nam_ix is an index into the string constant pool, and the ns_ix is an index into the namespace constant pool.
    RTQ_NAME = 0x0F     # Runtime Multiname - nam_ix here, and then ns from Stack at R/T
    RTQ_NAME_A = 0x10   # Runtime Multiname - nam_ix here, and then ns from Stack at R/T
    RTQ_NAME_L = 0x11   # Runtime Multiname - then both nam & ns from  Stack at R/T
    RTQ_NAME_LA = 0x12  # Runtime Multiname - then both nam & ns from  Stack at R/T
    MULTINAME = 0x09    # Multiname - nam_ix & ns_set_ix
    MULTINAME_A = 0x0E  # Multiname - nam_ix & ns_set_ix
    MULTINAME_L = 0x1B  # Runtime Multiname Late - ns_set_ix, then nam from Stack at R/T
    MULTINAME_LA = 0x1C # Runtime Multiname Late - ns_set_ix, then nam from Stack at R/T
    TYPE_NAME = 0x1D # not in the AVM2 overview docs I've seen - BEW 2023-11-23


class MethodFlags(IntFlag):
    NONE = 0x00
    NEED_ARGUMENTS = 0x01
    NEED_ACTIVATION = 0x02
    NEED_REST = 0x04
    HAS_OPTIONAL = 0x08
    IGNORE_REST = 0x10
    EXPLICIT = 0x20
    SET_DXNS = 0x40
    HAS_PARAM_NAMES = 0x80


class ConstantKind(IntEnum):
    INT = 0x03
    UINT = 0x04
    DOUBLE = 0x06
    UTF8 = 0x01
    TRUE = 0x0B
    FALSE = 0x0A
    NULL = 0x0C
    UNDEFINED = 0x00
    NAMESPACE = 0x08
    PACKAGE_NAMESPACE = 0x16
    PACKAGE_INTERNAL_NS = 0x17
    PROTECTED_NAMESPACE = 0x18
    EXPLICIT_NAMESPACE = 0x19
    STATIC_PROTECTED_NS = 0x1A
    PRIVATE_NS = 0x05
    MULTINAME = 0x09


class ClassFlags(IntFlag):
    DYNAMIC = 0x00
    SEALED = 0x01
    FINAL = 0x02
    INTERFACE = 0x04
    PROTECTED_NS = 0x08


class TraitKind(IntEnum):
    SLOT = 0
    METHOD = 1
    GETTER = 2
    SETTER = 3
    CLASS = 4
    FUNCTION = 5
    CONST = 6


class TraitAttributes(IntFlag):
    FINAL = 0x01
    OVERRIDE = 0x02
    METADATA = 0x04
