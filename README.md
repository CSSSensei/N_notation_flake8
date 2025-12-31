# flake8-n-notation

Flake8 plugin enforcing **N-notation** (ultra-strict).

## Install (editable)

```bash
python -m pip install -e .
```

## Run

Only show N-notation errors:

```bash
python -m flake8 --select NNO .
```

Show N-notation errors + other flake8 checks:

```bash
python -m flake8 .
```

## Tests

Run all tests (unittest discovery):

```bash
python -m unittest discover -s tests -v
```

## Codes (current)

Project-level:
- `NNO401`: filename must be `n<digits>.py`
- `NNO500`: repository README must contain the exact N-notation declaration block

AST-level:
- `NNO101`: invalid variable name
- `NNO104`: invalid function name
- `NNO106`: invalid class name
- `NNO107`: derived class name must match base class naming chain
- `NNO108` / `NNO109`: invalid member names (`n_...` / `_n...`)
- `NNO110`: invalid loop/comprehension iterator name (must be `n`, `nn`, ...)
- `NNO201` / `NNO202`: invalid parameter names
- `NNO210`: invalid method receiver name (`self` replacement must be `n<ClassName[1:]>`)
- `NNO602`: docstrings forbidden
- `NNO701`: variable annotations forbidden

Token-level:
- `NNO601`: comments forbidden (exception: `# noqa` / `# noqa: ...` allowed)
- imports:
  - `NNO301`: `import X as N1` alias required
  - `NNO302` / `NNO303`: `from X import Y as N0000000001` alias required (10 digits)
  - `NNO310`: import groups order invalid (stdlib → third_party → local)
  - `NNO311`: blank line separation between groups invalid
  - `NNO312`: numeric ordering inside group invalid

## Notes

- Plugin is intentionally strict and may flag non-N-notation code (including `__init__.py`).
- Use `# noqa: NNO...` for local suppressions when necessary.
