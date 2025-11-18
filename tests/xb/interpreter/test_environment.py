import pytest

import xb.interpreter.value as v
from xb.interpreter.environment import Environment
from xb.interpreter.errors import XbRuntimeError
from xb.interpreter.value import Op


def test_getitem_raises_keyerror_for_missing_key():
    env = Environment()
    with pytest.raises(XbRuntimeError):
        _ = env["undefined_key"]


def test_setitem_raises_keyerror_for_missing_key():
    env = Environment()
    with pytest.raises(XbRuntimeError):
        env["undefined_key"] = v.Boolean(True)


def test_setitem_raises_keyerror_for_const_key():
    env = Environment()
    env.declare_const("const", v.Number(5))

    with pytest.raises(XbRuntimeError):
        env["const"] = v.Number(6)


def test_setitem_works_for_variable_key():
    env = Environment()
    env.declare_var("var", v.Number(5))

    env["var"] = v.Number(8)

    assert Op.eq(env["var"], v.Number(8))


def test_getitem_works():
    env = Environment()
    env.declare_const("const", v.Number(1))
    env.declare_var("var", v.String("hey"))

    assert Op.eq(env["const"], v.Number(1))
    assert Op.eq(env["var"], v.String("hey"))


def test_getitem_resolves_parent_var():
    parent_env = Environment()
    parent_env.declare_const("parent_var", v.Number(42))

    env = Environment(parent_env)

    assert Op.eq(env["parent_var"], v.Number(42))


def test_getitem_shadows_parent_var():
    parent_env = Environment()
    parent_env.declare_const("var", v.Number(42))

    env = Environment(parent_env)
    env.declare_var("var", v.Number(44))

    assert Op.eq(env["var"], v.Number(44))


def test_setitem_sets_parent_var():
    parent_env = Environment()
    parent_env.declare_var("parent_var", v.Number(45))

    env = Environment(parent_env)
    env["parent_var"] = v.Number(46)

    assert Op.eq(env["parent_var"], v.Number(46))
    assert Op.eq(parent_env["parent_var"], v.Number(46))


def test_cannot_redeclare_name():
    env = Environment()
    env.declare_const("value", v.Number(5))

    with pytest.raises(XbRuntimeError):
        env.declare_var("value", v.Number(6))
