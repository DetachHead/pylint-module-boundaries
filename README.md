# pylint module boundaries

a pylint plugin to enforce boundaries between modules in your project. similar to nx's
[enforce-module-boundaries](https://nx.dev/core-features/enforce-project-boundaries) eslint plugin

## example

say you have three packages in your project: `common`, `package1` and `package2`. you want `package1` and
`package2` to be able to import from the `common` package, but you don't want to
allow `common` to import anything from the them, which would cause problems like circular
dependencies.

to fix this, you can define a `banned-imports` rule to allow pylint to detect such a thing:
![](readme-images/img.png)

see [usage](/#usage) below for a config example

## installing

this package is not yet published on pypi. for now just install it from github:

```toml
# pyproject.toml
[tool.poetry.group.dev.dependencies]
pylint-module-boundaries = { git = "https://github.com/DetachHead/pylint-module-boundaries.git", rev = "master" }
```

## usage
```toml
# pyproject.toml
[tool.pylint.MASTER]
load-plugins = "pylint_module_boundaries"
# (currently uses regex but i want to replace it with something better in the future)
banned-imports = '''
{
    "common(\\..*)?": "package1(\\..*)?",
    "common(\\..*)?": "package2(\\..*)?"
}
'''
```