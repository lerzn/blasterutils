from functools import singledispatch, update_wrapper

from blasterutils.generaltools import logger


def command_dispatch(func):
    registry = {}

    def unregistered_command(bot, update, *args, **kwargs):
        return

    def dispatch(command):
        nonlocal registry

        try:
            impl = registry[command]
        except KeyError:
            logger.warning(f"Unregistered command: {command}")
            return unregistered_command

        return impl

    def register(command, func=None):
        nonlocal registry

        if func is None:
            return lambda c: register(command, c)

        registry[command] = func

        return func

    def wrapper(bot, update, *args, **kwargs):
        text = update.message.text
        if len(text.split()) == 1:
            command = text
        else:
            command = text.split()[0]
            kwargs['args'] = text.split()[1:]

        return dispatch(command)(bot, update, *args, **kwargs)

    registry[object] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = registry
    update_wrapper(wrapper, func)

    return wrapper

