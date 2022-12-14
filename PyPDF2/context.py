from typing import Union
import contextvars

_current_context_var: contextvars.ContextVar = contextvars.ContextVar('pypdf2_context')


class Context(object):
    def __init__(self, decimal_precision: Union[int, None]=None):
        self.decimal_precision = decimal_precision

    def copy(self) -> 'Context':
        cp = Context(decimal_precision=self.decimal_precision)
        return cp


def get_context() -> Context:
    try:
        return _current_context_var.get()
    except LookupError:
        context = Context()
        _current_context_var.set(context)
        return context


def set_context(context: Context):
    if context in (DefaultContext, AcrobatContext):
        context = context.copy()
    _current_context_var.set(context)


DefaultContext = Context(decimal_precision=None)
AcrobatContext = Context(decimal_precision=19)
