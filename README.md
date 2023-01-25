# pylint module boundaries

a pylint plugin to enforce boundaries between modules in your project. similar to nx's [enforce-module-boundaries eslint plugin](https://nx.dev/core-features/enforce-project-boundaries)

## installing

this package is not yet published on pypi. for now just install it from github:

```toml
# pyproject.toml
[tool.poetry.group.dev.dependencies]
module-boundaries = { git = "https://github.com/DetachHead/pylint-module-boundaries.git", rev = "master" }
```

## usage

enable the plugin:

```toml
# pyproject.toml
[tool.pylint.MASTER]
load-plugins = "module_boundaries"
```
