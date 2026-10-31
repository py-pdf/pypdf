Constants
---------

## Deprecated names

The following names remain available with a ``DeprecationWarning`` until
pypdf 7.0.0. Use the uppercase replacement shown here:

* ``TypArguments`` -> ``TypeArguments``
* ``TypFitArguments`` -> ``FitTypes``
* ``FileSpecificationDictionaryEntries.Type``, ``Mac``, ``Unix``, and ``Cl``
    -> ``TYPE``, ``MAC``, ``UNIX``, and ``CL``
* ``FilterTypeAbbreviations.AHx`` -> ``AHX``
* ``GraphicsStateParameters.OP``, ``op``, ``CA``, and ``ca`` ->
    ``OP_STROKING``, ``OP_NON_STROKING``, ``CA_STROKING``, and
    ``CA_NON_STROKING`` respectively.
* ``AnnotationDictionaryAttributes.Type``, ``Subtype``, ``Rect``,
    ``Contents``, ``Border``, and ``StructParent`` -> ``TYPE``, ``SUBTYPE``,
    ``RECT``, ``CONTENTS``, ``BORDER``, and ``STRUCT_PARENT``
* ``InteractiveFormDictEntries.Fields``, ``NeedAppearances``, and ``SigFlags``
    -> ``FIELDS``, ``NEED_APPEARANCES``, and ``SIG_FLAGS``
* ``FieldDictionaryAttributes.Parent``, ``Kids``, ``Ff``, and ``Opt``
    -> ``PARENT``, ``KIDS``, ``FF``, and ``OPT``
* ``FieldDictionaryAttributes.FfBits`` members are changing to uppercase:
    ``ReadOnly`` -> ``READ_ONLY``, ``Required`` -> ``REQUIRED``, ``NoExport`` ->
    ``NO_EXPORT``, ``Multiline`` -> ``MULTILINE``, ``Password`` -> ``PASSWORD``,
    ``NoToggleToOff`` -> ``NO_TOGGLE_TO_OFF``, ``Radio`` -> ``RADIO``,
    ``Pushbutton`` -> ``PUSHBUTTON``, ``Combo`` -> ``COMBO``, ``Edit`` ->
    ``EDIT``, ``Sort`` -> ``SORT``, ``FileSelect`` -> ``FILE_SELECT``,
    ``MultiSelect`` -> ``MULTI_SELECT``, ``DoNotSpellCheck`` ->
    ``DO_NOT_SPELL_CHECK``, ``DoNotScroll`` -> ``DO_NOT_SCROLL``, ``Comb`` ->
    ``COMB``, ``RadiosInUnison`` -> ``RADIOS_IN_UNISON``, ``RichText`` ->
    ``RICH_TEXT``, and ``CommitOnSelChange`` -> ``COMMIT_ON_SEL_CHANGE``.
* ``OutlineFontFlag.italic`` and ``.bold`` -> ``ITALIC`` and ``BOLD``.
* ``CheckboxRadioButtonAttributes.Opt`` -> ``OPT``

``FieldDictionaryAttributes.FfBits.RADIOS_IN_UNISON`` and ``RICH_TEXT`` use
the same PDF flag bit, as their legacy names did; they are semantic aliases,
not a naming collision.

.. autoclass:: pypdf.constants.TypeArguments
        :members:
        :undoc-members:
        :show-inheritance:

.. autoclass:: pypdf.constants.FitTypes
        :members:
        :undoc-members:
        :show-inheritance:

The stroking and non-stroking graphics-state keys differ only by case in the
PDF syntax (``/OP`` vs. ``/op`` and ``/CA`` vs. ``/ca``). The semantic
replacement names preserve that distinction explicitly.

.. autoclass:: pypdf.constants.AnnotationFlag
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pypdf.constants.ImageType
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pypdf.constants.PageLabelStyle
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pypdf.constants.UserAccessPermissions
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pypdf.constants.FieldDictionaryAttributes
       :members:
       :undoc-members:
    :exclude-members: FT, Parent, PARENT, Kids, KIDS, T, TU, TM, Ff, FF, V, DV, AA, Opt, OPT, attributes, attributes_dict
       :show-inheritance:
