# flake-aod

Flake8 extension to check comments against Azure DevOps tickets. The plugin checks that:
1. Every comment with a reference to an ADO item (`AB#12345`) has a corresponding item.
2. ADO items are references in a proper format (`ADO: AB#12345`)
3. TODO items with ADO annotation have assigned item (`TODO: AB#12345`).

Example:
```python
class Foo:
    def foo(self) -> None: # TODO: AB#12345
        pass # ab 12345
```
```bash
>> flake8

```