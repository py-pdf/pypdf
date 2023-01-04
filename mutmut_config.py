"""
Configuration for mutmut.

See https://mutmut.readthedocs.io/en/latest/
"""


def pre_mutation(context):
    line = context.current_source_line.strip()
    if (
        "_codecs" in context.filename
        or "pragma: no cover" in line
        or "deprecate" in line
        or line.startswith("logger")
    ):
        context.skip = True
