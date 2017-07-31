#
# Copyright (C) 2011, 2012 Pablo Barenbaum <foones@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""Definition of Gobstones builtin functions, procedures and constants."""

import sys

from lang.gbs_type import (
    BasicTypes,
    GbsTypeVar,
    GbsTupleType,
    GbsBoolType,
    GbsIntType,
    GbsColorType,
    GbsDirType,
    GbsFunctionType,
    GbsProcedureType,
    GbsForallType,
    GbsListType,
)
from lang.gbs_constructs import (
    RenameConstruct,
    BuiltinConstant,
    BuiltinFunction,
    BuiltinProcedure,
)

import common.i18n as i18n
from common.utils import (
    DynamicException,
)

#### Definition of built-in functions and constants.

class GbsRuntimeException(DynamicException):
    """Base exception for Gobstones runtime errors."""

    def error_type(self):
        "Description of the exception type."
        return i18n.i18n('Runtime error')

TYPEVAR_X = GbsTypeVar()

# a -> a
TYPE_AA = GbsForallType(
            [TYPEVAR_X],
            GbsFunctionType(
                GbsTupleType([TYPEVAR_X]),
                GbsTupleType([TYPEVAR_X])))

# a x a -> Bool
TYPE_AAB = GbsForallType(
                [TYPEVAR_X],
                GbsFunctionType(
                    GbsTupleType([TYPEVAR_X, TYPEVAR_X]),
                    GbsTupleType([GbsBoolType()])))

# Int x Int -> Int
TYPE_III = GbsFunctionType(
            GbsTupleType([GbsIntType(), GbsIntType()]),
            GbsTupleType([GbsIntType()]))

# Bool x Bool -> Bool
TYPE_BBB = GbsFunctionType(
                GbsTupleType([GbsBoolType(), GbsBoolType()]),
                GbsTupleType([GbsBoolType()]))

# Bool -> Bool
TYPE_BB = GbsFunctionType(
                GbsTupleType([GbsBoolType()]),
                GbsTupleType([GbsBoolType()]))

class GbsEnum(object):
    """Represents an enumerated type."""

    def __init__(self, i):
        self._ord = i

    def enum_type(self):
        """Subclasses should implement the method to return the name
        of the enumerated type."""
        raise Exception("Subclass responsibility")

    def enum_size(self):
        """Subclasses should implement the method to return the number
        of elements in the enumerated type."""
        raise Exception("Subclass responsibility")

    def next(self):
        """Returns the next element in the enumerated type. (Wrap around
        if the maximum is reached)."""
        return self.__class__((self._ord + 1) % self.enum_size())

    def prev(self):
        """Returns the previous element in the enumerated type. (Wrap around
        if the minimum is reached)."""
        return self.__class__((self._ord - 1) % self.enum_size())

    def opposite(self):
        """Returns the opposite element in the enumerated type.
        Currently only works for enums of an even number of elements,
        returning the opposite element if they were in a circle."""
        new_i = (self._ord + self.enum_size() / 2) % self.enum_size()
        return self.__class__(new_i)

    def ord(self):
        """Returns the ord of the instance in the enumerated type."""
        return self._ord

    def __eq__(self, other):
        return isinstance(other, GbsEnum) and \
               self.enum_type() == other.enum_type() and \
               self._ord == other.ord()

#### Directions

DIRECTION_NAMES = [
    i18n.i18n('North'),
    i18n.i18n('East'),
    i18n.i18n('South'),
    i18n.i18n('West'),
]

DIRECTION_DELTA = {
    0: (1, 0),
    1: (0, 1),
    2: (-1, 0),
    3: (0, -1),
}

class Direction(GbsEnum):
    "Represents a Gobstones direction."

    def enum_type(self):
        "Return the name of the enumerated type."
        return 'Dir'

    def enum_size(self):
        "Return the size of the enumerated type."
        return 4

    def delta(self):
        "Return the delta for this direction."
        return DIRECTION_DELTA[self.ord()]

    def __repr__(self):
        return DIRECTION_NAMES[self.ord()]

NORTH = Direction(0)
EAST  = Direction(1)
SOUTH = Direction(2)
WEST  = Direction(3)

#### Colors

COLOR_NAMES = [
    i18n.i18n('Color0'),
    i18n.i18n('Color1'),
    i18n.i18n('Color2'),
    i18n.i18n('Color3'),
]

class Color(GbsEnum):
    "Represents a Gobstones color."

    def enum_type(self):
        "Return the name of the enumerated type."
        return 'Color'

    def enum_size(self):
        "Return the size of the enumerated type."
        return 4

    def name(self):
        "Return the name of this color."
        return COLOR_NAMES[self.ord()]

    def __repr__(self):
        return self.name()

NUM_COLORS = 4
COLOR0 = Color(0)
COLOR1 = Color(1)
COLOR2 = Color(2)
COLOR3 = Color(3)

def isinteger(value):
    "Return True iff the given Python value is integral."
    if sys.version_info[0] < 3:
        return isinstance(value, int) or isinstance(value, long)
    else:
        return isinstance(value, int)

def isenum(value):
    "Return True iff x is instance of a Gobstones enumerated type."
    return isinstance(value, bool) or \
           isinstance(value, Color) or \
           isinstance(value, Direction)

def poly_typeof(value):
    "Return the name of the type of the value."
    if isinstance(value, bool):
        return 'Bool'
    elif isinteger(value):
        return 'Int'
    elif isinstance(value, list):
        assert False
    else:
        return value.enum_type()

def poly_next(value):
    "Return the next value of the same type as the one given."
    if isinstance(value, bool):
        return not value
    elif isinteger(value):
        return value + 1
    elif isinstance(value, list):
        return [poly_next(elem) for elem in value]
    else:
        return value.next()

def poly_prev(value):
    "Return the previous value of the same type as the one given."
    if isinstance(value, bool):
        return not value
    elif isinteger(value):
        return value - 1
    elif isinstance(value, list):
        return [poly_prev(elem) for elem in value]
    else:
        return value.prev()

def poly_opposite(value):
    "Return the opposite value of the same type as the one given."
    if isinstance(value, bool):
        return not value
    elif isinteger(value):
        return -value
    elif isinstance(value, list):
        return [poly_opposite(elem) for elem in value]
    else:
        return value.opposite()

def gbs_poly_opposite(global_state, value):
    """Gobstones builtin function for the opposite value. Works only
    for directions and integers; raises a GbsRuntimeException if that
    is not the case."""
    if poly_typeof(value) not in ['Dir', 'Int']:
        msg = i18n.i18n(
            'The argument to opposite should be a direction or an integer')
        raise GbsRuntimeException(msg, global_state.area())
    else:
        return poly_opposite(value)

def poly_ord(value):
    """Returns a list of integers representing the ord of the given
    Gobstones value."""
    if isinstance(value, bool):
        if not value:
            return [0]
        else:
            return [1]
    elif isinteger(value):
        return [value]
    elif isinstance(value, list):
        return [poly_ord(elem) for elem in value]
    else:
        return [value.ord()]

def poly_cmp(global_state, value1, value2, relop):
    """Returns True iff the given relational operator holds for
    the Gobstones values."""
    if poly_typeof(value1) != poly_typeof(value2):
        msg = i18n.i18n(
            'Relational operation between values of different types')
        raise GbsRuntimeException(msg, global_state.area())
    return relop(poly_ord(value1), poly_ord(value2))

def arith_add(_, x, y):
    "Add the numbers."
    return x + y

def arith_sub(_, x, y):
    "Subtract the numbers."
    return x - y

def arith_mul(_, x, y):
    "Multiply the numbers."
    return x * y

def arith_pow(global_state, x, y):
    "Return x power y. Check for negative exponents."
    if y < 0:
        msg = global_state.backtrace(i18n.i18n('Negative exponent'))
        raise GbsRuntimeException(msg, global_state.area())
    else:
        return x ** y

def arith_div(global_state, x, y):
    "Return x div y. Check for zero division."
    if y == 0:
        msg = global_state.backtrace(i18n.i18n('Division by zero'))
        raise GbsRuntimeException(msg, global_state.area())
    else:
        return x / y

def arith_mod(global_state, x, y):
    "Return x mod y. Check for zero division."
    if y == 0:
        msg = global_state.backtrace(i18n.i18n('Division by zero'))
        raise GbsRuntimeException(msg, global_state.area())
    else:
        return x % y

def arith_op(opr, global_state, *values):
    """Given an n-ary arithmetic operator, and n values, return
    the result, dynamically checking that the values are all of the
    right Int type. If that is not the case, raise a GbsRuntimeException."""
    for value in values:
        if poly_typeof(value) != 'Int':
            msg = i18n.i18n('Arithmetic operation over non-numeric values')
            raise GbsRuntimeException(msg, global_state.area())
    return opr(global_state, *values)

def logical_op(opr, global_state, *values):
    """Given an n-ary logical operator, and n values, return
    the result, dynamically checking that the values are all of the
    right Bool type. If that is not the case, raise a GbsRuntimeException."""
    for value in values:
        if poly_typeof(value) != 'Bool':
            msg = i18n.i18n('Logical operation over non-boolean values')
            raise GbsRuntimeException(msg, global_state.area())
    return opr(global_state, *values)

def logical_not(_, value):
    "Return the logical negation of the given value."
    return not value

def logical_and(_, value1, value2):
    "Return the logical conjunction of the values."
    return value1 and value2

def logical_or(_, value1, value2):
    "Return the logical disjunction of the values."
    return value1 or value2

def board_put_stone(global_state, color):
    """Put a stone in the board."""
    if poly_typeof(color) != 'Color':
        msg = i18n.i18n('The argument to PutStone should be a color')
        raise GbsRuntimeException(msg, global_state.area())
    global_state.board.put_stone(color)

def board_take_stone(global_state, color):
    """Take a stone from the board."""
    if poly_typeof(color) != 'Color':
        msg = i18n.i18n('The argument to TakeStone should be a color')
        raise GbsRuntimeException(msg, global_state.area())
    if global_state.board.num_stones(color) > 0:
        global_state.board.take_stone(color)
    else:
        msg = global_state.backtrace(
            i18n.i18n('Cannot take stones of color %s') % (color,))
        raise GbsRuntimeException(msg, global_state.area())

def board_move(global_state, direction):
    """Move the head."""
    if poly_typeof(direction) != 'Dir':
        msg = i18n.i18n('The argument to Move should be a direction')
        raise GbsRuntimeException(msg, global_state.area())
    if global_state.board.can_move(direction):
        global_state.board.move(direction)
    else:
        msg = global_state.backtrace(
            i18n.i18n('Cannot move to %s') % (direction,))
        raise GbsRuntimeException(msg, global_state.area())

def board_num_stones(global_state, color):
    """Number of stones of the given color."""
    if poly_typeof(color) != 'Color':
        msg = i18n.i18n('The argument to numStones should be a color')
        raise GbsRuntimeException(msg, global_state.area())
    return global_state.board.num_stones(color)

def board_exist_stones(global_state, color):
    """Return True iff there are stones of the given color."""
    if poly_typeof(color) != 'Color':
        msg = i18n.i18n('The argument to existStones should be a color')
        raise GbsRuntimeException(msg, global_state.area())
    return global_state.board.exist_stones(color)

def board_can_move(global_state, direction):
    """Return True iff the head can move to the given direction."""
    if poly_typeof(direction) != 'Dir':
        msg = i18n.i18n('The argument to canMove should be a direction')
        raise GbsRuntimeException(msg, global_state.area())
    return global_state.board.can_move(direction)

# 'Main',
BUILTINS = [

    #### Procedures

    BuiltinProcedure(
        i18n.i18n('PutStone'),
        GbsProcedureType(GbsTupleType([GbsColorType()])),
        board_put_stone
    ),

    BuiltinProcedure(
        i18n.i18n('TakeStone'),
        GbsProcedureType(GbsTupleType([GbsColorType()])),
        board_take_stone
    ),

    BuiltinProcedure(
        i18n.i18n('Move'),
        GbsProcedureType(GbsTupleType([GbsDirType()])),
        board_move
    ),

    BuiltinProcedure(
        i18n.i18n('GoToOrigin'),
        GbsProcedureType(GbsTupleType([])),
        lambda global_state: global_state.board.go_to_origin()
    ),

    BuiltinProcedure(
        i18n.i18n('ClearBoard'),
        GbsProcedureType(GbsTupleType([])),
        lambda global_state: global_state.board.clear_board()
    ),

    #### Functions

    BuiltinFunction(
        i18n.i18n('numStones'),
        GbsFunctionType(
            GbsTupleType([GbsColorType()]),
            GbsTupleType([GbsIntType()])),
        board_num_stones
    ),

    BuiltinFunction(
        i18n.i18n('existStones'),
        GbsFunctionType(
            GbsTupleType([GbsColorType()]),
            GbsTupleType([GbsBoolType()])),
        board_exist_stones
    ),

    BuiltinFunction(
        i18n.i18n('canMove'),
        GbsFunctionType(
            GbsTupleType([GbsDirType()]),
            GbsTupleType([GbsBoolType()])),
        board_can_move
    ),

    BuiltinFunction(
        i18n.i18n('minBool'),
        GbsFunctionType(
            GbsTupleType([]),
            GbsTupleType([GbsBoolType()])),
        lambda global_state: False
    ),

    BuiltinFunction(
        i18n.i18n('maxBool'),
        GbsFunctionType(
            GbsTupleType([]),
            GbsTupleType([GbsBoolType()])),
        lambda global_state: True
    ),

    BuiltinFunction(
        i18n.i18n('minDir'),
        GbsFunctionType(GbsTupleType([]), GbsTupleType([GbsDirType()])),
        lambda global_state: NORTH
    ),

    BuiltinFunction(
        i18n.i18n('maxDir'),
        GbsFunctionType(GbsTupleType([]), GbsTupleType([GbsDirType()])),
        lambda global_state: WEST
    ),

    BuiltinFunction(
        i18n.i18n('minColor'),
        GbsFunctionType(GbsTupleType([]), GbsTupleType([GbsColorType()])),
        lambda global_state: COLOR0
    ),

    BuiltinFunction(
        i18n.i18n('maxColor'),
        GbsFunctionType(GbsTupleType([]), GbsTupleType([GbsColorType()])),
        lambda global_state: COLOR3
    ),

    BuiltinFunction(
        i18n.i18n('next'),
        TYPE_AA,
        lambda global_state, x: poly_next(x)
    ),
    BuiltinFunction(
        i18n.i18n('prev'),
        TYPE_AA,
        lambda global_state, x: poly_prev(x)
    ),
    BuiltinFunction(
        i18n.i18n('opposite'),
        TYPE_AA,
        gbs_poly_opposite
    ),

    #### Operators

    ## Relational operators

    BuiltinFunction(
        i18n.i18n('=='),
        TYPE_AAB,
        lambda global_state, x, y:
            poly_cmp(global_state, x, y, lambda a, b: a == b)
    ),

    BuiltinFunction(
        i18n.i18n('/='),
        TYPE_AAB,
        lambda global_state, x, y:
            poly_cmp(global_state, x, y, lambda a, b: a != b)
    ),
    BuiltinFunction(
        i18n.i18n('<'),
        TYPE_AAB,
        lambda global_state, x, y:
            poly_cmp(global_state, x, y, lambda a, b: a < b)
    ),
    BuiltinFunction(
        i18n.i18n('<='),
        TYPE_AAB,
        lambda global_state, x, y:
            poly_cmp(global_state, x, y, lambda a, b: a <= b)
    ),
    BuiltinFunction(
        i18n.i18n('>='),
        TYPE_AAB,
        lambda global_state, x, y:
            poly_cmp(global_state, x, y, lambda a, b: a >= b)
    ),
    BuiltinFunction(
        i18n.i18n('>'),
        TYPE_AAB,
        lambda global_state, x, y:
            poly_cmp(global_state, x, y, lambda a, b: a > b)
    ),

    ## Logical operators
    ##
    ## NOTE: logical operators in Gobstones are not
    ##       short-circuiting

    BuiltinFunction(
        i18n.i18n('not'),
        TYPE_BB,
        lambda global_state, x:
            logical_op(logical_not, global_state, x)
    ),
    BuiltinFunction(
        i18n.i18n('&&'),
        TYPE_BBB,
        lambda global_state, x, y:
            logical_op(logical_and, global_state, x, y)
    ),
    BuiltinFunction(
        i18n.i18n('||'),
        TYPE_BBB,
        lambda global_state, x, y:
            logical_op(logical_or, global_state, x, y)
    ),

    # Arithmetic operators

    BuiltinFunction(
        i18n.i18n('+'),
        TYPE_III,
        lambda global_state, x, y:
            arith_op(arith_add, global_state, x, y)
    ),
    BuiltinFunction(
        i18n.i18n('-'),
        TYPE_III,
        lambda global_state, x, y:
            arith_op(arith_sub, global_state, x, y)
    ),
    BuiltinFunction(
        i18n.i18n('*'),
        TYPE_III,
        lambda global_state, x, y:
            arith_op(arith_mul, global_state, x, y)
    ),
    BuiltinFunction(
        i18n.i18n('^'),
        TYPE_III,
        lambda global_state, x, y:
            arith_op(arith_pow, global_state, x, y)
    ),
    BuiltinFunction(
        i18n.i18n('div'),
        TYPE_III,
        lambda global_state, x, y:
            arith_op(arith_div, global_state, x, y)
    ),
    BuiltinFunction(
        i18n.i18n('mod'),
        TYPE_III,
        lambda global_state, x, y:
        arith_op(arith_mod, global_state, x, y)
    ),
    BuiltinFunction(
        i18n.i18n('unary-'),
        TYPE_AA,
        gbs_poly_opposite
    ),

    #### Constants

    BuiltinConstant(i18n.i18n('True'), GbsBoolType(), True),
    BuiltinConstant(i18n.i18n('False'), GbsBoolType(), False),
    BuiltinConstant(i18n.i18n('North'), GbsDirType(), NORTH),
    BuiltinConstant(i18n.i18n('South'), GbsDirType(), SOUTH),
    BuiltinConstant(i18n.i18n('East'), GbsDirType(), EAST),
    BuiltinConstant(i18n.i18n('West'), GbsDirType(), WEST),
    BuiltinConstant(i18n.i18n('Color0'), GbsColorType(), COLOR0),
    BuiltinConstant(i18n.i18n('Color1'), GbsColorType(), COLOR1),
    BuiltinConstant(i18n.i18n('Color2'), GbsColorType(), COLOR2),
    BuiltinConstant(i18n.i18n('Color3'), GbsColorType(), COLOR3),
]

#### List functions

TYPE_NIL = GbsForallType(
                [TYPEVAR_X],
                GbsFunctionType(
                    GbsTupleType([]),
                    GbsTupleType([GbsListType(TYPEVAR_X)])))

TYPE_CONS = GbsForallType(
                [TYPEVAR_X],
                GbsFunctionType(
                    GbsTupleType([TYPEVAR_X, GbsListType(TYPEVAR_X)]),
                    GbsTupleType([GbsListType(TYPEVAR_X)])))

TYPE_SNOC = GbsForallType(
                [TYPEVAR_X],
                GbsFunctionType(
                    GbsTupleType([GbsListType(TYPEVAR_X), TYPEVAR_X]),
                    GbsTupleType([GbsListType(TYPEVAR_X)])))

TYPE_IS_NIL = GbsForallType(
                [TYPEVAR_X],
                GbsFunctionType(
                    GbsTupleType([GbsListType(TYPEVAR_X)]),
                    GbsTupleType([GbsBoolType()])))

TYPE_HEAD_LAST = GbsForallType(
                    [TYPEVAR_X],
                    GbsFunctionType(
                        GbsTupleType([GbsListType(TYPEVAR_X)]),
                        GbsTupleType([TYPEVAR_X])))

TYPE_TAIL_INIT = GbsForallType(
                    [TYPEVAR_X],
                    GbsFunctionType(
                        GbsTupleType([GbsListType(TYPEVAR_X)]),
                        GbsTupleType([GbsListType(TYPEVAR_X)])))

def list_operation(global_state, lst, f):
    """Wrapper for list operations that require the list not to be
empty (head, tail, init, last).
"""
    if len(lst) == 0:
        msg = global_state.backtrace(i18n.i18n('Empty list'))
        raise GbsRuntimeException(msg, global_state.area())
    else:
        return f(lst)

def list_head(global_state, lst):
    "Return the first element of the list."
    return list_operation(global_state, lst, lambda lst: lst[0])

def list_tail(global_state, lst):
    "Return the tail of the list."
    return list_operation(global_state, lst, lambda lst: lst[1:])

def list_last(global_state, lst):
    "Return the last element of the list."
    return list_operation(global_state, lst, lambda lst: lst[-1])

def list_init(global_state, lst):
    "Return the initial segment of the list."
    return list_operation(global_state, lst, lambda lst: lst[:-1])

LIST_BUILTINS = [
    BuiltinFunction(
        i18n.i18n('nil'),
        TYPE_NIL,
        lambda global_state: []
    ),
    BuiltinFunction(
        i18n.i18n('cons'),
        TYPE_CONS,
        lambda global_state, x, xs: [x] + xs
    ),
    BuiltinFunction(
        i18n.i18n('snoc'),
        TYPE_SNOC,
        lambda global_state, xs, x: xs + [x]
    ),
    BuiltinFunction(
        i18n.i18n('isNil'),
        TYPE_IS_NIL,
        lambda global_state, x: len(x) == 0
    ),
    BuiltinFunction(
        i18n.i18n('head'),
        TYPE_HEAD_LAST,
        list_head
    ),
    BuiltinFunction(
        i18n.i18n('last'),
        TYPE_HEAD_LAST,
        list_last
    ),
    BuiltinFunction(
        i18n.i18n('tail'),
        TYPE_TAIL_INIT,
        list_tail
    ),
    BuiltinFunction(
        i18n.i18n('init'),
        TYPE_TAIL_INIT,
        list_init
    ),
]

def _is_int_constant(string):
    """Return True if the string represents an integer constant.
    - It can start with a minus sign.
    - It should have at least one digit.
    - The remaining elements should all be digits in 0..9."""
    digs = '0123456789'
    if len(string) == 0 or (string[0] == '-' and len(string) == 1):
        return False
    if string[0] not in '-' + digs:
        return False
    for char in string[1:]:
        if char not in digs:
            return False
    return True
        
#### Uncomment to enable the list extensions.
#BUILTINS += LIST_BUILTINS

####

COLORS_BY_INITIAL = {
    i18n.i18n('Color0')[0].lower(): COLOR0,
    i18n.i18n('Color1')[0].lower(): COLOR1,
    i18n.i18n('Color2')[0].lower(): COLOR2,
    i18n.i18n('Color3')[0].lower(): COLOR3,
}

def _color_name_to_index_dict():
    """Return a dictionary mapping color names to color index.
    Color names are accepted in various forms:
    - capitalized (Rojo)
    - lowercase (rojo)
    - upper initial (R)
    - lower initial (r)
    The index is the order of the color in the Color enumerated
    type."""
    dic = {}
    for coli in range(NUM_COLORS):
        name = Color(coli).name()
        dic[name] = coli
        dic[name.lower()] = coli
        dic[name[0]] = coli
        dic[name[0].lower()] = coli
        dic[coli] = coli
    return dic

COLOR_NAME_TO_INDEX_DICT = _color_name_to_index_dict()

#### Polymorphic builtins

BUILTINS_POLYMORPHIC = {
    i18n.i18n('next'): True,
    i18n.i18n('prev'): True,
    i18n.i18n('opposite'): True,
    i18n.i18n('unary-'): True,
}

def poly_encode_type(type_name):
    """Return an encoding of the given type name."""
    return type_name

def polyname(fname, types):
    """Given a function name and a list of types, return a
    "polymorphic function name", which corresponds to the concrete
    function name that is going to be called when applying the
    function to arguments of those types. For instance, when
    applying siguiente to an integer, the polyname might be
    something like "siguiente@Int"."""
    return fname + '@' + '@'.join([poly_encode_type(typ) for typ in types])

def polyname_name(name):
    """Given the polyname of a function, return the original
    function name."""
    return name.split('@')[0]

def polyname_types(name):
    """Given the polyname of a function, return the names of
    the types of its arguments."""
    return name.split('@')[1:]

def _poly_args(builtin):
    """Given a builtin function or procedure, successively
    yield all possible instantiations of the types of its
    parameters. For a monomorphic function, this yields a single
    list of parameter types. For a polymorphic function, the
    number of possible parameter types could grow exponentially
    on the number of parameters."""
    def gen(length):
        """Generate all possible lists of parameter types, of the
        given length."""
        if length == 0:
            yield []
        else:
            for param_types in gen(length - 1):
                for basic_type in BasicTypes.keys():
                    yield [basic_type] + param_types
    for param_types in gen(len(builtin.gbstype().parameters())):
        yield param_types

def _initialize_poly_builtins():
    """Add one builtin function/procedure for each polyname of
    every polymorphic builtin function/procedure."""
    for builtin in BUILTINS:
        if builtin.name() not in BUILTINS_POLYMORPHIC:
            continue
        for param_types in _poly_args(builtin):
            pname = polyname(builtin.name(), param_types)
            BUILTINS.append(RenameConstruct(pname, builtin))

_initialize_poly_builtins()

BUILTIN_NAMES = [b.name() for b in BUILTINS]

CORRECT_NAMES = BUILTIN_NAMES + ['Main']

BUILTINS_BY_NAME = {}

def _initialize_builtins_by_name():
    """Initialize the dictionary of builtins mapping builtin
    names to constructs."""
    for builtin in BUILTINS:
        BUILTINS_BY_NAME[builtin.name()] = builtin

_initialize_builtins_by_name()

##

def parse_constant(string):
    """Given a string that represents a Gobstones constant, return
    an object representing that value."""
    if _is_int_constant(string):
        return int(string)
    if string in BUILTINS_BY_NAME:
        return BUILTINS_BY_NAME[string].primitive()
    else:
        return None

