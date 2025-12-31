class ErrorCodes:
    # Project-level
    NNO401 = "filename expected n<digits>.py got {name}"
    NNO500 = "readme-declaration missing-or-mismatch"

    # AST-level: naming
    NNO101 = "var-name invalid got {name}"
    NNO104 = "func-name invalid got {name}"
    NNO106 = "class-name invalid got {name}"
    NNO107 = "derived-class base expected {expected}"

    # AST-level: members
    NNO108 = "member-name invalid got {name}"
    NNO109 = "member-name invalid got {name}"

    # AST-level: iterators
    NNO110 = "iterator invalid got {name}"

    # AST-level: parameters / receiver
    NNO201 = "param required expected {expected} got {name}"
    NNO202 = "param optional expected n<10digits/bits> got {name}"
    NNO210 = "method-self expected {expected} got {name}"

    # AST-level: type annotations
    NNO701 = "type annotation forbidden"

    # Text noise
    NNO601 = "comment forbidden"
    NNO602 = "docstring forbidden"

    # Directories
    NNO420 = "directory-name invalid got {name} (expected N<digits>[_<digits>]...)"

    # Imports
    NNO301 = "import requires alias N<k> (example: import os as N1)"
    NNO302 = "from-import requires alias N<10 digits> (example: from typing import List as N0000000001)"
    NNO303 = "from-import alias must be N<10 digits> (example: ... as N0000000001)"
    NNO310 = "import groups order invalid"
    NNO311 = "import group separation invalid"
    NNO312 = "import ordering invalid"
