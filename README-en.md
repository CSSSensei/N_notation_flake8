<h1 align="center">N notation linter</h1>
<p align="center">
<b>Following the principles is easy now!</b>

</p><p align="center">
<img src="https://img.shields.io/badge/made%20by-CSSSensei-1591EA" >
<img src="https://img.shields.io/badge/Phasalo-000FFF">
<img src="https://img.shields.io/badge/coverage-92％-000080">
<img src="https://img.shields.io/badge/version-N1n0.0-0000FF">
</p>

<p align="center">
    <a href="README.md">Русский</a> | English
</p>

## N-notation declaration

This repository uses **N notation** — a system of naming and encoding rules
based on numeric identifiers.

Using this notation is a deliberate architectural decision.

Identifiers of files, directories, variables, functions, classes, and other program entities
are not intended for semantic interpretation.

Attempts to “improve readability” by changing identifiers,
introducing verbal names, or adapting the code to other naming styles
are considered a violation of the project’s architectural integrity.

The project maintainers are not responsible for misinterpretations of the code structure
resulting from ignoring this notice.

For more details, see the [documentation](https://github.com/Phasalo/N_notation)

# Quick start

### Install

```bash
python -m pip install -e .
```

### Run the linter

Show only N-notation errors:

```bash
python -m flake8 --select NNO .
```

Show N-notation errors + other flake8 checks:

```bash
python -m flake8 .
```

### Tests

Run all tests:

```bash
python -m unittest discover -s tests -v
```

## Codes (current)

### Project-level:

* `NNO401`: filename must be `n<digits>.py`
* `NNO500`: repository README must contain the **exact** N-notation declaration block

### AST-level:

* `NNO101`: invalid variable name
* `NNO104`: invalid function name
* `NNO106`: invalid class name
* `NNO107`: derived class name must match base class naming chain
* `NNO108` / `NNO109`: invalid member names (`n_...` / `_n...`)
* `NNO110`: invalid loop/comprehension iterator name (must be `n`, `nn`, ...)
* `NNO201` / `NNO202`: invalid parameter names
* `NNO210`: invalid method receiver name (`self` replacement must be `n<ClassName[1:]>`)
* `NNO602`: docstrings forbidden
* `NNO701`: variable annotations forbidden

### Token-level:

* `NNO601`: comments forbidden
  (exception: `# noqa` / `# noqa: ...` are allowed)
* Imports:

  * `NNO301`: alias required: `import X as N1`
  * `NNO302` / `NNO303`: alias required: `from X import Y as N0000000001` (10 digits)
  * `NNO310`: import groups order invalid
    (stdlib → third_party → local)
  * `NNO311`: blank line separation between groups invalid
  * `NNO312`: numeric ordering inside group invalid

> [!NOTE]
> * Plugin is intentionally strict and may flag non-N-notation code
  (including `__init__.py`).
> * Use `# noqa: NNO...` for local suppressions when necessary.

---

<p align="center">
<b>Phasalo</b><br>
<i>Делаем красиво!</i><br><br>
2026
</p>
