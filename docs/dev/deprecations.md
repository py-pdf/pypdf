# Deprecations

PyPDF2 strives to be an excellent library for its current users and for new
ones. We are careful with introducing potentially breaking changes, but we
will do them if they provide value for the community on the long run.

## How to Deprecate

Assume the current version of PyPDF2 is `x.y.z`. After a discussion (e.g. via
Github issues) we decided to remove a class / function / method. This is how
we do it:

1. `x.y.(z+1)`: Add a PendingDeprecationWarning. If there is a replacement,
   the replacement is also introduced and the warning informs about the change
   and when it will happen.
   The docs let users know about the deprecation and when it will happen and the new function.
   The CHANGELOG informs about it.
2. `(x+1).0.0`: The PendingDeprecationWarning is changed to a DeprecationWarning.
   The CHANGELOG informs about it.
3. `(x+2).0.0`: The code and the DeprecationWarnings are removed.
   The CHANGELOG informs about it.

This means the users have 3 warnings in the CHANGELOG, a PendingDeprecationWarning
until the next major release and a DeprecationWarning until the major release
after that.

Please note that adding warnings can be a breaking change for some users; most
likely just in the CI.
This means it needs to be properly documented.
