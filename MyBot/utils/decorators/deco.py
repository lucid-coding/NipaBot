import disnake
import asyncio
from functools import wraps
import asyncio
import functools
import types
import typing as t
from contextlib import suppress

from discord import Member, NotFound
from discord.ext import commands
from discord.ext.commands import Cog, Context

from disnake.ext.commands import check, Context

def restrict_to_user(user: int):
    """Allows only specific user to run these commands. Must be edited manually from files"""
    async def predicate(ctx: Context):
        return ctx.author.id == user
    return check(predicate)


"""Utilities for interaction with functions."""

import functools
import inspect
import types
import typing as t

from logging import getLogger

log = getLogger(__name__)

Argument = t.Union[int, str]
BoundArgs = t.OrderedDict[str, t.Any]
Decorator = t.Callable[[t.Callable], t.Callable]
ArgValGetter = t.Callable[[BoundArgs], t.Any]
DEBUG_MODE = False


class GlobalNameConflictError(Exception):
    """Raised when there's a conflict between the globals used to resolve annotations of wrapped and its wrapper."""


def get_arg_value(name_or_pos: Argument, arguments: BoundArgs) -> t.Any:
    """
    Return a value from `arguments` based on a name or position.
    `arguments` is an ordered mapping of parameter names to argument values.
    Raise TypeError if `name_or_pos` isn't a str or int.
    Raise ValueError if `name_or_pos` does not match any argument.
    """
    if isinstance(name_or_pos, int):
        # Convert arguments to a tuple to make them indexable.
        arg_values = tuple(arguments.items())
        arg_pos = name_or_pos

        try:
            name, value = arg_values[arg_pos]
            return value
        except IndexError:
            raise ValueError(f"Argument position {arg_pos} is out of bounds.")
    elif isinstance(name_or_pos, str):
        arg_name = name_or_pos
        try:
            return arguments[arg_name]
        except KeyError:
            raise ValueError(f"Argument {arg_name!r} doesn't exist.")
    else:
        raise TypeError("'arg' must either be an int (positional index) or a str (keyword).")


def get_arg_value_wrapper(
    decorator_func: t.Callable[[ArgValGetter], Decorator],
    name_or_pos: Argument,
    func: t.Callable[[t.Any], t.Any] = None,
) -> Decorator:
    """
    Call `decorator_func` with the value of the arg at the given name/position.
    `decorator_func` must accept a callable as a parameter to which it will pass a mapping of
    parameter names to argument values of the function it's decorating.
    `func` is an optional callable which will return a new value given the argument's value.
    Return the decorator returned by `decorator_func`.
    """
    def wrapper(args: BoundArgs) -> t.Any:
        value = get_arg_value(name_or_pos, args)
        if func:
            value = func(value)
        return value

    return decorator_func(wrapper)


def get_bound_args(func: t.Callable, args: t.Tuple, kwargs: t.Dict[str, t.Any]) -> BoundArgs:
    """
    Bind `args` and `kwargs` to `func` and return a mapping of parameter names to argument values.
    Default parameter values are also set.
    """
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    return bound_args.arguments


def update_wrapper_globals(
        wrapper: types.FunctionType,
        wrapped: types.FunctionType,
        *,
        ignored_conflict_names: t.Set[str] = frozenset(),
) -> types.FunctionType:
    """
    Update globals of `wrapper` with the globals from `wrapped`.
    For forwardrefs in command annotations discordpy uses the __global__ attribute of the function
    to resolve their values, with decorators that replace the function this breaks because they have
    their own globals.
    This function creates a new function functionally identical to `wrapper`, which has the globals replaced with
    a merge of `wrapped`s globals and the `wrapper`s globals.
    An exception will be raised in case `wrapper` and `wrapped` share a global name that is used by
    `wrapped`'s typehints and is not in `ignored_conflict_names`,
    as this can cause incorrect objects being used by discordpy's converters.
    """
    annotation_global_names = (
        ann.split(".", maxsplit=1)[0] for ann in wrapped.__annotations__.values() if isinstance(ann, str)
    )
    # Conflicting globals from both functions' modules that are also used in the wrapper and in wrapped's annotations.
    shared_globals = set(wrapper.__code__.co_names) & set(annotation_global_names)
    shared_globals &= set(wrapped.__globals__) & set(wrapper.__globals__) - ignored_conflict_names
    if shared_globals:
        raise GlobalNameConflictError(
            f"wrapper and the wrapped function share the following "
            f"global names used by annotations: {', '.join(shared_globals)}. Resolve the conflicts or add "
            f"the name to the `ignored_conflict_names` set to suppress this error if this is intentional."
        )

    new_globals = wrapper.__globals__.copy()
    new_globals.update((k, v) for k, v in wrapped.__globals__.items() if k not in wrapper.__code__.co_names)
    return types.FunctionType(
        code=wrapper.__code__,
        globals=new_globals,
        name=wrapper.__name__,
        argdefs=wrapper.__defaults__,
        closure=wrapper.__closure__,
    )


def command_wraps(
        wrapped: types.FunctionType,
        assigned: t.Sequence[str] = functools.WRAPPER_ASSIGNMENTS,
        updated: t.Sequence[str] = functools.WRAPPER_UPDATES,
        *,
        ignored_conflict_names: t.Set[str] = frozenset(),
) -> t.Callable[[types.FunctionType], types.FunctionType]:
    """Update the decorated function to look like `wrapped` and update globals for discordpy forwardref evaluation."""
    def decorator(wrapper: types.FunctionType) -> types.FunctionType:
        return functools.update_wrapper(
            update_wrapper_globals(wrapper, wrapped, ignored_conflict_names=ignored_conflict_names),
            wrapped,
            assigned,
            updated,
        )

    return decorator

def respect_role_hierarchy(member_arg: Argument) -> t.Callable:
    """
    Ensure the highest role of the invoking member is greater than that of the target member.
    If the condition fails, a warning is sent to the invoking context. A target which is not an
    instance of discord.Member will always pass.
    `member_arg` is the keyword name or position index of the parameter of the decorated command
    whose value is the target member.
    This decorator must go before (below) the `command` decorator.
    """
    def decorator(func: types.FunctionType) -> types.FunctionType:
        @command_wraps(func)
        async def wrapper(*args, **kwargs) -> None:
            log.info(f"{func.__name__}: respect role hierarchy decorator called")

            bound_args = get_bound_args(func, args, kwargs)
            target = get_arg_value(member_arg, bound_args)

            if not isinstance(target, Member):
                log.info("The target is not a discord.Member; skipping role hierarchy check.")
                await func(*args, **kwargs)
                return

            ctx = get_arg_value(1, bound_args)
            cmd = ctx.command.name
            actor = ctx.author

            if target.top_role >= actor.top_role:
                log.info(
                    f"{actor} ({actor.id}) attempted to {cmd} "
                    f"{target} ({target.id}), who has an equal or higher top role."
                )
                await ctx.send(
                    f":x: {actor.mention}, you may not {cmd} "
                    "someone with an equal or higher top role."
                )
            else:
                log.info(f"{func.__name__}: {target.top_role=} < {actor.top_role=}; calling func")
                await func(*args, **kwargs)
        return wrapper
    return decorator

def has_no_roles(*roles: t.Union[str, int]) -> t.Callable:
    """
    Returns True if the user does not have any of the roles specified.
    `roles` are the names or IDs of the disallowed roles.
    """
    async def predicate(ctx: Context) -> bool:
        try:
            await commands.has_any_role(*roles).predicate(ctx)
        except commands.MissingAnyRole:
            return True
        else:
            # This error is never shown to users, so don't bother trying to make it too pretty.
            roles_ = ", ".join(f"'{item}'" for item in roles)
            raise commands.CheckFailure(f"You have at least one of the disallowed roles: {roles_}")

    return commands.check(predicate)

# 807624518909820958
# 807924308114407435
# 807626654184374302

def target_has_no_roles(*roles: t.Union[str, int]) -> t.Callable:
    async def predicate(ctx: Context) -> bool:
        return
