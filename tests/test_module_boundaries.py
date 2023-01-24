import json

import pylint.testutils
from astroid.builder import AstroidBuilder

import module_boundaries


class UniqueReturnCheckerTestCase(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = module_boundaries.ModuleBoundariesChecker

    node = AstroidBuilder().string_build(
        "from modules.bar import value", modname="modules.foo"
    )

    def visit(self):
        self.checker.visit_module(self.node)  # type:ignore[no-any-expr]


class TestBanned(UniqueReturnCheckerTestCase):
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": "modules\\.bar(\\..*)?",
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
            )
        ):
            self.visit()


class TestAllowed(UniqueReturnCheckerTestCase):
    def test_allowed_module(self):
        with self.assertNoMessages():
            self.visit()
