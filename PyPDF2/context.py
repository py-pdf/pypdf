import contextvars

_current_context_var = contextvars.ContextVar('pypdf2_context')

class Context(object):
    def __init__(self, prec=None):
        self.prec = prec

    def copy(self):
        cp = Context(prec=self.prec)
        return cp


def get_context():
    try:
        return _current_context_var.get()
    except LookupError:
        context = Context()
        _current_context_var.set(context)
        return context


def set_context(context):
    if context in (DefaultContext, AcrobatContext):
        context = context.copy()
    _current_context_var.set(context)


DefaultContext = Context(prec=None)
AcrobatContext = Context(prec=19)