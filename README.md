# pylint module boundaries

a pylint plugin to enforce boundaries between modules in your project. similar to nx's
[enforce-module-boundaries](https://nx.dev/core-features/enforce-project-boundaries) eslint plugin

## example

say you have three packages in your project - `common`, `package1`, and `package2` - you can use the `banned-imports` rule to prevent `common` from importing anything from `package1` or `package2`, thus avoiding issues such as circular dependencies.

Pylint can then be used to detect any violations of this rule:

![](https://github.com/DetachHead/pylint-module-boundaries/raw/master/readme-images/img.png)

see [usage](/#usage) below for a config example

## installing

```
poetry install pylint-module-boundaries
```

## usage

### `pyproject.toml` example

```toml
[tool.pylint.MASTER]
load-plugins = "pylint_module_boundaries"
banned-imports = '''
{
    "common(\\..*)?": ["package1(\\..*)?", "package2(\\..*)?"],
    "scripts(\\..*)?": ["package1(\\..*)?", "package2(\\..*)?"]
}
'''
banned-imports-check-usages = true
```

### options

| option                        | type      | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | default |
| ----------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| `banned-imports`              | `string`  | a JSON object pairing regexes matching modules to arrays of regexes matching modules that they are not allowed to import from. due to the limitations in config types allowed by pylint, this has to be a JSON object represented as a string.<br /><br />note that these regexes must be a full match, so to match any submodules you should append `(\\..*)?` to the regex (double `\` required because it's JSON).<br /><br />yes, i know this option is quite annoying to use but its purpose is to be as flexible as possible. i plan to add an easier to use option in the future that covers most basic use cases. see [this issue](https://github.com/DetachHead/pylint-module-boundaries/issues/10) | `{}`    |
| `banned-imports-check-usages` | `boolean` | whether usages of the imports should be checked as well as the imports themselves. works on imports of entire modules but can potentially cause false positives depending on your use case                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | `true`  |
