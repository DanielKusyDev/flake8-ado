# flake8-ado

Flake8 extension to check comments against Azure DevOps tickets. The plugin checks that:
1. Every comment with a reference to an ADO item (`AB#12345`) has a corresponding item.
2. ADO items are references in a proper format (`ADO: AB#12345`)
3. TODO items with ADO annotation have assigned item (`TODO: AB#12345`).

Example:
```python
# foo.py
class Foo:
    def foo(self) -> None: # TODO: AB#12345
        pass # ab 12345
```
```shell
>> flake8 --ado-access-token=<TOKEN> --ado_organization_url=<URL>
./foo.py:2:36: ADO001 Missing ADO item
```

## Installation
```shell
pip install flake8 flake8-ado
```

## Arguments
- `--ado-access-token` - Valid AzureDevOps token.
- `ado_organization_url` - AzureDevOps organization url e.g. https://dev.azure.com/foo.

## Errors
| Code   | Message                                           |
|--------|---------------------------------------------------|
| ADO001 | Missing ADO item                                  |
| ADO002 | Malformed item reference                          |
| ADO003 | Wrong capitalization (ADO and AB must be capital) |
| ADO004 | TODO needs the AOD item reference                 |

## Contribution
Feel free to modify the code. To start with the development you need poetry.
```shell
poetry install --with=dev
```