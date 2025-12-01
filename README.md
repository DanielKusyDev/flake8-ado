# flake8-ado

[![PyPI version](https://img.shields.io/pypi/v/flake8-ado.svg)](https://pypi.org/project/flake8-ado/)

Flake8 plugin that validates inline comments against Azure DevOps work items.

Use it when you want every `TODO` / `ADO` reference in code to actually point to a real work item — and to fail CI when someone leaves a sloppy comment without a ticket.

---

## What it does

`flake8-ado` scans comments and enforces a few rules:

1. Every comment with an ADO reference (`AB#12345`) must match an actual work item.
2. ADO references must follow a consistent format, e.g. `ADO: AB#12345`.
3. `TODO` comments that mention ADO must include a work item: `TODO: AB#12345`.

Example:

```python
# foo.py
class Foo:
    def foo(self) -> None:  # TODO: AB#12345
        pass  # ADO: AB#999999
```

Running:

```bash
flake8 \
  --ado-access-token=<PERSONAL_ACCESS_TOKEN> \
  --ado_organization_url=https://dev.azure.com/<ORG>
```

may produce:

```
./foo.py:2:36: ADO001 Missing ADO item
./foo.py:3:12: ADO002 Malformed or invalid ADO reference
```

---

## Installation

```bash
pip install flake8-ado
```

Ensure `flake8` and `flake8-ado` are installed in the same Python environment used locally or in CI.

---

## Usage

The plugin activates automatically when installed. Provide two extra flags:

```bash
flake8 \
  --ado-access-token=<PERSONAL_ACCESS_TOKEN> \
  --ado_organization_url=https://dev.azure.com/<ORG> \
  path/to/your/code
```

### Options

- `--ado-access-token` — Azure DevOps Personal Access Token with **read** access to work items.
- `--ado_organization_url` — Azure DevOps organization URL, e.g. `https://dev.azure.com/your-org`.

---

## Recognized patterns

The plugin detects ADO references inside comments.

**Plain ADO reference:**

```python
# ADO: AB#12345
```

**TODO with ADO reference:**

```python
# TODO: AB#12345
```

**Bare reference (discouraged but validated):**

```python
# AB#12345
```

Malformed or invalid references produce errors.

---

## Error codes

- `ADO001` — missing or non-existing ADO item
- `ADO002` — malformed ADO reference
- `ADO003` — invalid format or capitalization
- `ADO004` — TODO without an ADO item reference

You can ignore codes like any other Flake8 rule:

```bash
flake8 --ignore=ADO004 ...
```

---

## CI integration

Typical steps:

1. Store your ADO PAT as a secret (e.g. `ADO_PAT`).
2. Install `flake8` and `flake8-ado`.
3. Run Flake8 with the ADO flags.

Example:

```bash
pip install flake8-ado

flake8 \
  --ado-access-token="$ADO_PAT" \
  --ado_organization_url="https://dev.azure.com/your-org" \
  src/
```

If a reference is invalid, CI fails.

---

## Development

```bash
git clone https://github.com/DanielKusyDev/flake8-ado.git
cd flake8-ado

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
pytest
```

Run locally against test code:

```bash
flake8 \
  --ado-access-token=<TOKEN> \
  --ado_organization_url=<URL> \
  tests/example_project
```

---

## Why

Teams often try to enforce "every TODO must link to a work item" as a soft rule. It lasts a week.

`flake8-ado` automates it: if the ticket doesn’t exist or the reference is malformed, the build fails.

---

## License

MIT
