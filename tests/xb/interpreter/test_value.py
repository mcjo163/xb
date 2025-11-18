import pytest
from lark import Token

import xb.interpreter.ast as t
from xb.interpreter.environment import Environment
from xb.interpreter.errors import XbRuntimeError
from xb.interpreter.value import Boolean, Empty, Number, Op, String


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
