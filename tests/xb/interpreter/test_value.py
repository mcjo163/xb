import pytest
from lark import Token

import xb.interpreter.ast as t
from xb.interpreter.environment import Environment
from xb.interpreter.errors import XbRuntimeError
from xb.interpreter.value import Array, Boolean, Empty, Number, Object, Op, String


# Empty
def test_empty_parsing():
    node, env = t.Empty(), Environment()
    e = Empty.from_node(node, env)

    assert Op.eq(e, Empty())


def test_empty_casting():
    with pytest.raises(XbRuntimeError):
        Empty.cast(Boolean(False))


def test_empty_display():
    assert Empty().display() == "()"


def test_empty_equality():
    assert Op.eq(Empty(), Empty())
    assert not Op.neq(Empty(), Empty())
    assert Op.neq(Empty(), Boolean(False))


# Boolean
def test_bool_parsing():
    env = Environment()
    node_true = t.Bool(Token("BOOL", "true"))
    node_false = t.Bool(Token("BOOL", "false"))

    assert Op.eq(Boolean.from_node(node_true, env), Boolean(True))
    assert Op.eq(Boolean.from_node(node_false, env), Boolean(False))


def test_bool_casting():
    assert Op.eq(Boolean.cast(Empty()), Boolean(False))
    assert Op.neq(Boolean.cast(Boolean(True)), Boolean(False))
    assert Op.eq(Boolean.cast(Boolean(False)), Boolean(False))


def test_bool_display():
    assert Boolean(True).display() == "true"
    assert Boolean(False).display() == "false"


def test_bool_equality():
    assert Op.eq(Boolean(True), Boolean(True))
    assert Op.eq(Boolean(False), Boolean(False))
    assert Op.neq(Boolean(True), Boolean(False))
    assert Op.neq(Boolean(False), Boolean(True))


# String
def test_string_parsing():
    env = Environment()
    node = t.String(Token("STRING", '"hello world"'))

    assert Op.eq(String.from_node(node, env), String("hello world"))


def test_string_casting():
    assert Op.eq(String.cast(Empty()), String("()"))
    assert Op.eq(String.cast(Boolean(True)), String("true"))
    assert Op.eq(String.cast(Boolean(False)), String("false"))
    assert Op.eq(String.cast(String("hi")), String("hi"))


def test_string_display():
    assert String("").display() == '""'
    assert String("\"what\"").display() == '""what""'


def test_string_equality():
    assert Op.eq(String("hi"), String("hi"))
    assert Op.neq(String("hi"), String("bye"))
    assert Op.neq(String("true"), Boolean(True))


def test_string_comparison():
    assert Op.gt(String("d"), String("a"))
    assert Op.lt(String("b"), String("bc"))
    assert Op.lte(String("b"), String("b"))
    assert Op.gte(String("b"), String("B"))

    with pytest.raises(XbRuntimeError):
        Op.lt(String("one"), Number(1))


def test_string_concat():
    assert Op.eq(Op.add(String("one"), String("two")), String("onetwo"))


# Number
def test_number_parsing():
    env = Environment()
    (
        hex_0xFF,
        int_from_float_1000,
        int_40,
        int_from_float_00,
        float_5p5,
    ) = map(
        lambda node: Number.from_node(node, env),
        (t.Number(Token("SIGNED_NUMBER", s)) for s in [
            "0xFF",
            "1e3",
            "40",
            "0.0",
            "5.5",
        ]),
    )

    assert Op.eq(hex_0xFF, Number(0xFF))
    assert Op.eq(int_from_float_1000, Number(1e3))
    assert Op.eq(int_40, Number(40))
    assert Op.eq(int_from_float_00, Number(0.0))
    assert Op.eq(float_5p5, Number(5.5))

    assert type(int_from_float_1000._val) is int
    assert type(int_from_float_00._val) is int
    assert type(float_5p5._val) is float


def test_number_casting():
    assert Op.eq(Number.cast(String("0xFF")), Number(255))
    assert Op.eq(Number.cast(Number(1)), Number(1))

    with pytest.raises(XbRuntimeError):
        Number.cast(Empty())
        Number.cast(Boolean(True))


def test_number_display():
    assert Number(5).display() == "5"
    assert Number(0xFF).display() == "255"
    assert Number(1.54).display() == "1.54"


def test_number_equality():
    assert Op.eq(Number(42), Number(42))
    assert Op.neq(Number(0), Number(-1))
    assert Op.eq(Number(5), Number(5.0))
    assert Op.neq(Number(1000), Boolean(True))
    assert Op.neq(Number(20), Empty())


def test_number_comparison():
    assert Op.lt(Number(5), Number(6.0))
    assert Op.lte(Number(5), Number(5.0))
    assert Op.gt(Number(5e2), Number(6.0))
    assert Op.gte(Number(5), Number(0))


def test_number_operation_sample():
    def do_op(op_fn, a, b, expected):
        assert Op.eq(op_fn(Number(a), Number(b)), Number(expected))

    do_op(Op.add, 1, 1, 1 + 1)
    do_op(Op.sub, 9.6, 8, 9.6 - 8)
    do_op(Op.mul, 4e7, 0xb, 4e7 * 0xb)
    do_op(Op.div, 8, 3, 8 / 3)
    do_op(Op.int_div, 8, 3, 8 // 3)
    do_op(Op.mod, 10, 2, 10 % 2)
    do_op(Op.pow, 4e2, 2, 4e2 ** 2)


# Array
def test_array_parsing():
    env = Environment()
    # TODO: test this after AST uses Values for everything


def test_array_cast():
    array = Array([Number(1)])
    array2 = Array.cast(array)
    assert len(array2._list) == 1

    with pytest.raises(XbRuntimeError):
        Array.cast(Number(1))


def test_array_display():
    assert Array([
        Number(1),
        String("hi"),
        Boolean(True),
    ]).display() == '[1, "hi", true]'

    assert Array([Array([])]).display() == "[[]]"


def test_array_equality():
    assert Op.eq(
        Array([
            Number(1),
            String("hi"),
        ]),
        Array([
            Number(1),
            String("hi"),
        ]),
    )


def test_array_access():
    array = Array([Number(1), String("hi")])
    assert Op.eq(array.index_get(Number(1)), String("hi"))

    array.index_set(Number(1), String("bye"))
    assert Op.eq(array.index_get(Number(1)), String("bye"))

    with pytest.raises(XbRuntimeError):
        array.index_get(Number(10))

    with pytest.raises(XbRuntimeError):
        array.index_get(Number(10.5))

    with pytest.raises(XbRuntimeError):
        array.index_set(String("10"), String("see ya"))


# Object
def test_object_parsing():
    env = Environment()
    # TODO: test this after AST uses Values for everything


def test_object_cast():
    obj = Object({ "sample": Object.Entry(Number(5), False) })
    obj2 = Object.cast(obj)
    assert len(obj2._dict.items()) == 1

    with pytest.raises(XbRuntimeError):
        Object.cast(Number(1))


def test_object_display():
    assert Object({
        "number": Object.Entry(Number(1), True),
        "string": Object.Entry(String("hi"), False),
        "boolean": Object.Entry(Boolean(True), False)
    }).display() == '{number : 1, string = "hi", boolean = true}'

    assert Array([Array([])]).display() == "[[]]"
    assert Object({ "nested": Object.Entry(Object({}), True) }).display() == "{nested : {}}"


def test_object_equality():
    assert Op.eq(
        Object({
            "number": Object.Entry(Number(1), True),
            "string": Object.Entry(String("hi"), False),
            "boolean": Object.Entry(Boolean(True), False)
        }),
        Object({
            "number": Object.Entry(Number(1), True),
            "string": Object.Entry(String("hi"), False),
            "boolean": Object.Entry(Boolean(True), False)
        }),
    )


def test_object_access():

    obj = Object({
        "number": Object.Entry(Number(1), True),
        "string": Object.Entry(String("hi"), False),
        "boolean": Object.Entry(Boolean(True), False)
    })
    assert Op.eq(obj.key_get("number"), Number(1))
    assert Op.eq(obj.key_get("string"), String("hi"))

    obj.key_set("string", String("bye"))
    assert Op.eq(obj.key_get("string"), String("bye"))

    with pytest.raises(XbRuntimeError):
        obj.key_get("fake")

    with pytest.raises(XbRuntimeError):
        obj.index_get(Number(10))

    with pytest.raises(XbRuntimeError):
        obj.key_set("10", String("see ya"))

    with pytest.raises(XbRuntimeError):
        obj.key_set("number", Number(2))
