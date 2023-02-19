import json
import re
from typing import cast

from astroid import nodes
from pylint.checkers.base_checker import BaseChecker
from pylint.lint import PyLinter


class ModuleBoundariesChecker(BaseChecker):
    msgs = {
        "E5000": (
            "this module (`%s`) is not allowed to import from `%s`",
            "banned-imports",
            "used to enforce module boundaries in your project.",
        )
    }

    options = (
        (
            "banned-imports",
            {
                "default": "{}",
                "type": "string",
                "metavar": "<a json object where the keys are regex patterns for modules that are not allowwed to import from the corresponding values' regex pattens>",
                "help": 'for example: `{"foo.*": "bar.*"}` means that modules starting with "foo" can not import from modules starting with "bar"',
            },
        ),
    )
    banned_imports: dict[re.Pattern[str], list[re.Pattern[str]]]

    def open(self):
        self.banned_imports = {
            re.compile(key): [re.compile(value) for value in values]
            for key, values in cast(
                dict[str, str],
                json.loads(
                    self.linter.config.banned_imports  # type:ignore[no-any-expr]
                ),
            ).items()
        }

    def _visit_import(self, node: nodes.Import | nodes.ImportFrom):
        # type is wrong here? i don't think it can be `None` but actually the attribute doesn't exist
        if not hasattr(node, "modname"):
            return
        current_module = node.root().name
        for module_regex in (
            re.match(key, current_module) and key for key in self.banned_imports.keys()
        ):
            if (
                module_regex
                and node.modname
                and any(
                    re.match(value, node.modname)
                    for value in self.banned_imports[module_regex]
                )
            ):
                self.add_message(
                    "banned-imports", node=node, args=(current_module, node.modname)
                )

    def visit_importfrom(self, node: nodes.ImportFrom):
        self._visit_import(node)

    def visit_import(self, node: nodes.Import):
        self._visit_import(node)


def register(linter: PyLinter) -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """
    linter.register_checker(ModuleBoundariesChecker(linter))
