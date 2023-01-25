import json
import re
from typing import cast

from astroid import nodes
from pylint.checkers.base_checker import BaseChecker
from pylint.lint import PyLinter


class ModuleBoundariesChecker(BaseChecker):
    msgs = {
        "E0001": (
            "banned imports",
            "banned-imports",
            "this module is not allowed to import from that module",
        )
    }

    options = (
        (
            "banned-imports",
            {
                "default": "{}",
                "type": "string",
                "metavar": "<some nonsense>",
                "help": "todo lol",
            },
        ),
    )

    # TODO: make this a lazily loaded property or something
    def banned_imports(self) -> dict[re.Pattern[str], re.Pattern[str]]:
        return {
            re.compile(key): re.compile(value)
            for key, value in cast(
                dict[str, str],
                json.loads(
                    self.linter.config.banned_imports  # type:ignore[no-any-expr]
                ),
            ).items()
        }

    def visit_module(self, node: nodes.Module):
        banned_imports = self.banned_imports()
        for child in node.get_children():  # type:ignore[func-returns-value]
            try:
                module_regex = next(
                    re.match(key, node.name) and key for key in banned_imports.keys()
                )
            except StopIteration:
                module_regex = None
            if (
                isinstance(child, (nodes.Import, nodes.ImportFrom))
                and module_regex
                and child.modname
                and re.match(banned_imports[module_regex], child.modname)
            ):
                self.add_message("banned-imports", node=child)


def register(linter: PyLinter) -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """
    linter.register_checker(ModuleBoundariesChecker(linter))
