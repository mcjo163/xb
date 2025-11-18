import pytest
from xb.interpreter.environment import Environment
from xb.interpreter.errors import XbRuntimeError


def test_getitem_raises_keyerror_for_missing_key():
    env = Environment()
    with pytest.raises(XbRuntimeError):
        _ = env["undefined_key"]


def test_setitem_raises_keyerror_for_missing_key():
    env = Environment()
    with pytest.raises(XbRuntimeError):
        env["undefined_key"] = True


def test_setitem_raises_keyerror_for_const_key():
    env = Environment()
    env.declare_const("const", 5)

    with pytest.raises(XbRuntimeError):
        env["const"] = 6


def test_setitem_works_for_variable_key():
    env = Environment()
    env.declare_var("var", 5)

    env["var"] = 8

    assert env["var"] == 8


def test_getitem_works():
    env = Environment()
    env.declare_const("const", 1)
    env.declare_var("var", "hey")

    assert env["const"] == 1
    assert env["var"] == "hey"


def test_getitem_resolves_parent_var():
    parent_env = Environment()
    parent_env.declare_const("parent_var", 42)

    env = Environment(parent_env)

    assert env["parent_var"] == 42


def test_getitem_shadows_parent_var():
    parent_env = Environment()
    parent_env.declare_const("var", 42)

    env = Environment(parent_env)
    env.declare_var("var", 44)

    assert env["var"] == 44


def test_setitem_sets_parent_var():
    parent_env = Environment()
    parent_env.declare_var("parent_var", 45)

    env = Environment(parent_env)
    env["parent_var"] = 46

    assert env["parent_var"] == 46
    assert parent_env["parent_var"] == 46


def test_cannot_redeclare_name():
    env = Environment()
    env.declare_const("value", 5)

    with pytest.raises(XbRuntimeError):
        env.declare_var("value", 6)
