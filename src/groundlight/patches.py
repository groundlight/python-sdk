"""
Some of the generated code has bugs, unfortunately. We can add hacky patches here,
so they're isolated outside the generated code.

The alternatives seem worse / more difficult:
- manually change the generated code, and then have to remember to undo the change any time we run `make generate`
- fork the openapi-generator code and fix the template bugs upstream
- submit PRs to the openapi-generator repo, and hope they get accepted
"""

from openapi_client.schemas import BoolClass, NoneClass, Singleton


def singleton_repr_patch(self):
    """
    This is a patch for printing representations of NoneClass and BoolClass. If we don't apply this patch,
    and we try to print() any field that has a value `None`, it will go into an infinite loop (RecursionError). Lol.

    Following this PR fix:
    https://github.com/OpenAPITools/openapi-generator/pull/12157/files#diff-dd296d28c61bac60384c9710af2291a1a202c53cc5236b5e8fc4b04646b6e844R496
    """
    if isinstance(self, NoneClass):
        return f"<{self.__class__.__name__}: None>"
    elif isinstance(self, BoolClass):
        if (self.__class__, True) in self._instances:
            return f"<{self.__class__.__name__}: True>"
        return f"<{self.__class__.__name__}: False>"
    return f"<{self.__class__.__name__}: {self}>"  # Note that I use "self" instead of super().__repr__() (because super() isn't available here ...)


Singleton.__repr__ = singleton_repr_patch
