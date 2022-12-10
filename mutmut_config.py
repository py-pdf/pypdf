"""
Configuration for mutmut.

See https://mutmut.readthedocs.io/en/latest/
"""


def pre_mutation(context):
    if "_codecs" in context.filename:
        context.skip = True

    line = context.current_source_line.strip()
    if "pragma: no cover" in line:
        context.skip = True
    if "deprecate" in line:
        context.skip = True
    if line.strip().startswith("logger"):
        context.skip = True
