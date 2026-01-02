<h1 align="center">N Notation Linter</h1>
<p align="center">
<b>Following the principles is easy now!</b>

</p><p align="center">
<img src="https://img.shields.io/badge/made%20by-CSSSensei-1591EA" >
<img src="https://img.shields.io/badge/Phasalo-000FFF">
<img src="https://img.shields.io/badge/coverage-91％-000080">
<img src="https://img.shields.io/badge/version-N1n2.0-0000FF">
</p>

<p align="center">
    <a href="README.md">Русский</a> | English
</p>

This is a **flake8 plugin** that checks code against **N notation** rules.
Use it in projects where you actually write in this style (or want to quickly lint specific files/directories).

## N notation principles

This plugin checks the following N notation philosophy rules:

- **Names are non-semantic.** Meaning comes from structure and context, not verbal identifiers.
- **Case matters:** `N...` — structures/types, `n...` — data/executables.
- **Files:** `n<digits>.py` (see `NNO401`).
- **Directories:** `N<digits>[_<digits>]...` (see `NNO420`).
- **Variables / functions:** `n<10 digits>` (boolean: `n<10 bits>`).
- **Classes:** `N<10 digits>`, derived classes form a chain `N<id>n<id>...` (see `NNO105`, `NNO107`).
- **Class members:** `n_<...>` / `_n<...>`; method receiver is not `self` but `n<ClassId>` (see `NNO210`).
- **Loop/comprehension iterators:** `n`, `nn`, `nnn`, ...
- **Imports:** alias required + ordering/separation/sorting (see `NNO301–NNO312`).
- **Noise is forbidden:** comments and docstrings are forbidden (except `# noqa...`).

> [!IMPORTANT]
> * For the full specification see the [documentation](https://github.com/Phasalo/N_notation).

## Feature: name suggestion

If a naming rule is violated, the linter may suggest a valid identifier in the diagnostic message:

`... (suggest <name>)`

Example:

`NNO101 var-name invalid got count (suggest n0123456789)`

## Quick start

### Install

```bash
python -m pip install n-notation
```

### Run the linter

Show only N notation errors:

```bash
python -m flake8 --select NNO .
```

Show N notation errors + other flake8 checks:

```bash
python -m flake8 .
```

### Tests

Run all tests:

```bash
python -m unittest discover -s tests -v
```

## Error codes

### Project-level:

* `NNO401`: filename must be `n<digits>.py`
* `NNO500`: repository README must contain the **exact** N notation declaration block

### AST-level:

* `NNO101`: invalid variable name
* `NNO104`: invalid function name
* `NNO105`: when inheriting, class name must be derived (`N<id>n<id>...`)
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

<br>
<p align="center">
<b>Phasalo</b><br>
<i>Make it pretty!</i><br><br>
2026
</p>
