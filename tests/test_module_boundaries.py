import json

import pylint.testutils
from astroid.builder import AstroidBuilder

import pylint_module_boundaries


class UniqueReturnCheckerTestCase(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_module_boundaries.ModuleBoundariesChecker

    node = AstroidBuilder().string_build(
        "from modules.bar import value\nfrom modules.baz import value",
        modname="modules.foo",
    )

    def visit(self):
        self.checker.visit_module(self.node)  # type:ignore[no-any-expr]


class TestBanned(UniqueReturnCheckerTestCase):
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?"
                ],
            }
        )
    }

    def test_banned_module(self):
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(self.node.get_children()),  # type:ignore[func-returns-value]
                line=1,
                end_line=1,
                end_col_offset=30,
                col_offset=0,
                args=("modules.foo", "modules.bar"),
            )
        ):
            self.visit()


class TestMultipleBannedInOneFile(UniqueReturnCheckerTestCase):
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?",
                    "modules\\.baz(\\..*)?",
                ],
            }
        )
    }

    def test_banned_module(self):
        children = self.node.get_children()  # type:ignore[func-returns-value]
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(children),
                line=1,
                end_line=1,
                end_col_offset=29,
                col_offset=0,
                args=("modules.foo", "modules.bar"),
            ),
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(children),
                line=2,
                end_line=1,
                end_col_offset=29,
                col_offset=0,
                args=("modules.foo", "modules.baz"),
            ),
        ):
            self.visit()


class TestOneBannedInMultipleFiles(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_module_boundaries.ModuleBoundariesChecker

    nodes = [
        AstroidBuilder().string_build(
            "from modules.baz import value",
            modname="modules.foo",
        ),
        AstroidBuilder().string_build(
            "from modules.baz import value",
            modname="modules.bar",
        ),
    ]

    def visit(self):
        for node in self.nodes:
            self.checker.visit_module(node)  # type:ignore[no-any-expr]

    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.baz(\\..*)?",
                ],
                "modules\\.bar(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.baz(\\..*)?",
                ],
            }
        )
    }

    def test_banned_module(self):
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(
                    self.nodes[0].get_children()  # type:ignore[func-returns-value]
                ),
                line=1,
                end_line=1,
                end_col_offset=29,
                col_offset=0,
                args=("modules.foo", "modules.baz"),
            ),
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(
                    self.nodes[1].get_children()  # type:ignore[func-returns-value]
                ),
                line=1,
                end_line=1,
                end_col_offset=29,
                col_offset=0,
                args=("modules.bar", "modules.baz"),
            ),
        ):
            self.visit()


class TestAllowed(UniqueReturnCheckerTestCase):
    def test_allowed_module(self):
        with self.assertNoMessages():
            self.visit()
