import json
import re
from typing import Iterable, cast

from astroid import nodes
from pylint.checkers.base_checker import BaseChecker
from pylint.lint import PyLinter


class ModuleBoundariesChecker(BaseChecker):
    msgs = {
        "E5000": (
            "this module (`%s`) is not allowed to import `%s`",
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
                "metavar": (
                    "<a json object where the keys are regex patterns for modules that"
                    " are not allowed to import from the corresponding values' regex"
                    " pattens. the regexes must be a full match>"
                ),
                "help": (
                    'for example: `{"foo.*": "bar.*"}` means that modules starting with'
                    ' "foo" can not import from modules starting with "bar"'
                ),
            },
        ),
        (
            "banned-imports-check-usages",
            {
                "default": True,
                "type": "yn",
                "help": (
                    "whether usages of the imports should be checked as well as the"
                    " imports themselves. works on imports of entire modules but can"
                    " potentially cause false positives"
                ),
            },
        ),
    )
    banned_imports: dict[re.Pattern[str], list[re.Pattern[str]]]
    check_usages: bool

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
        self.check_usages = (
            self.linter.config.banned_imports_check_usages  # type:ignore[no-any-expr]
        )

    def _check_imports(self, node: nodes.NodeNG, import_full_names: Iterable[str]):
        current_module = node.root().name
        for module_regex in (
            re.fullmatch(key, current_module) and key
            for key in self.banned_imports.keys()
        ):
            for import_full_name in import_full_names:
                if (
                    module_regex
                    and import_full_name
                    and any(
                        re.fullmatch(value, import_full_name)
                        for value in self.banned_imports[module_regex]
                    )
                ):
                    self.add_message(
                        "banned-imports",
                        node=node,
                        args=(current_module, import_full_name),
                    )

    def visit_importfrom(self, node: nodes.ImportFrom):
        self._check_imports(
            node, [f"{node.modname}.{name}" for [name, _] in node.names]
        )

    def visit_import(self, node: nodes.Import):
        self._check_imports(node, [name for [name, _] in node.names])

    def visit_attribute(self, node: nodes.Attribute):
        if self.check_usages and isinstance(node.expr, nodes.Name):
            self._check_imports(node, [f"{node.expr.name}.{node.attrname}"])


def register(linter: PyLinter) -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """
    linter.register_checker(ModuleBoundariesChecker(linter))
