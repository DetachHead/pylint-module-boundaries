import json
from typing import cast

import pylint.testutils
from astroid import nodes
from astroid.builder import AstroidBuilder

import pylint_module_boundaries


class ModuleBoundariesTestCase(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_module_boundaries.ModuleBoundariesChecker

    node = AstroidBuilder().string_build(
        "from modules.bar import value\nfrom modules.baz import value",
        modname="modules.foo",
    )

    def visit(self):
        self.walk(self.node)


class TestImportFromBanned(ModuleBoundariesTestCase):
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?"
                ]
            }
        )
    }

    def test_import_from_banned_module(self):
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(self.node.get_children()),  # type:ignore[func-returns-value]
                line=1,
                end_line=1,
                end_col_offset=29,
                col_offset=0,
                args=("modules.foo", "modules.bar.value"),
            )
        ):
            self.visit()


class TestImportBanned(ModuleBoundariesTestCase):
    node = AstroidBuilder().string_build(
        "import modules.bar\nimport modules.baz", modname="modules.foo"
    )
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?"
                ]
            }
        )
    }

    def test_import_banned_module(self):
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(
                    self.node.get_children()  # type:ignore[func-returns-value]
                ),
                line=1,
                end_line=1,
                end_col_offset=18,
                col_offset=0,
                args=("modules.foo", "modules.bar"),
            )
        ):
            self.visit()


class TestMultipleBannedInOneFile(ModuleBoundariesTestCase):
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?",
                    "modules\\.baz(\\..*)?",
                ]
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
                args=("modules.foo", "modules.bar.value"),
            ),
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(children),
                line=2,
                end_line=2,
                end_col_offset=29,
                col_offset=0,
                args=("modules.foo", "modules.baz.value"),
            ),
        ):
            self.visit()


class TestOneBannedInMultipleFiles(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_module_boundaries.ModuleBoundariesChecker

    nodes = [
        AstroidBuilder().string_build(
            "from modules.baz import value", modname="modules.foo"
        ),
        AstroidBuilder().string_build(
            "from modules.baz import value", modname="modules.bar"
        ),
    ]

    def visit(self):
        for node in self.nodes:
            self.walk(node)

    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.baz(\\..*)?"
                ],
                "modules\\.bar(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.baz(\\..*)?"
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
                args=("modules.foo", "modules.baz.value"),
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
                args=("modules.bar", "modules.baz.value"),
            ),
        ):
            self.visit()


class TestAllowed(ModuleBoundariesTestCase):
    def test_allowed_module(self):
        with self.assertNoMessages():
            self.visit()


class TestConditionalImportBanned(ModuleBoundariesTestCase):
    node = AstroidBuilder().string_build(
        "if True:\n   from modules.bar import value\n   from modules.baz import value",
        modname="modules.foo",
    )
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?"
                ]
            }
        )
    }

    def test_conditional_import_banned_module(self):
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=cast(
                    nodes.If,
                    next(
                        self.node.get_children()  # type:ignore[func-returns-value]
                    ),
                ).body[0],
                line=2,
                end_line=2,
                end_col_offset=32,
                col_offset=3,
                args=("modules.foo", "modules.bar.value"),
            )
        ):
            self.visit()


class TestModuleImportBanned(ModuleBoundariesTestCase):
    node = AstroidBuilder().string_build(
        "from modules import bar\nfrom modules import baz", modname="modules.foo"
    )
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?"
                ]
            }
        )
    }

    def test_module_import_banned_module(self):
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(
                    self.node.get_children()  # type:ignore[func-returns-value]
                ),
                line=1,
                end_line=1,
                end_col_offset=23,
                col_offset=0,
                args=("modules.foo", "modules.bar"),
            )
        ):
            self.visit()


class TestMultipleModuleImportBanned(ModuleBoundariesTestCase):
    node = AstroidBuilder().string_build(
        "from modules import bar, baz", modname="modules.foo"
    )
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?"
                ]
            }
        )
    }

    def test_multiple_module_import_banned_module(self):
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=next(
                    self.node.get_children()  # type:ignore[func-returns-value]
                ),
                line=1,
                end_line=1,
                end_col_offset=28,
                col_offset=0,
                args=("modules.foo", "modules.bar"),
            )
        ):
            self.visit()


class TestNotFullMatchAllowed(ModuleBoundariesTestCase):
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.f(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.b(\\..*)?"
                ]
            }
        )
    }

    def test_not_full_match_allowed(self):
        with self.assertNoMessages():
            self.visit()


class TestUsageBanned(ModuleBoundariesTestCase):
    node = AstroidBuilder().string_build(
        "import modules\nmodules.bar\nmodules.baz", modname="modules.foo"
    )
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?"
                ]
            }
        )
    }

    def test_usage_banned(self):
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(  # type:ignore[no-any-expr]
                msg_id="banned-imports",
                node=cast(
                    nodes.Expr,
                    list(
                        self.node.get_children()  # type:ignore[func-returns-value]
                    )[
                        1
                    ],
                ).value,
                line=2,
                end_line=2,
                end_col_offset=11,
                col_offset=0,
                args=("modules.foo", "modules.bar"),
            )
        ):
            self.visit()


class TestUsageAllowed(ModuleBoundariesTestCase):
    node = AstroidBuilder().string_build(
        "import modules\nmodules.bar\nmodules.baz", modname="modules.foo"
    )
    CONFIG: dict[str, object] = {
        "banned_imports": json.dumps(
            {  # type:ignore[no-any-expr]
                "modules\\.foo(\\..*)?": [  # type:ignore[no-any-expr]
                    "modules\\.bar(\\..*)?"
                ]
            }
        ),
        "banned_imports_check_usages": False,
    }

    def test_usage_allowed(self):
        with self.assertNoMessages():
            self.visit()
