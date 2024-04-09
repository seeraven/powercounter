"""
SML types.

Copyright:
    2024 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of powercounter (https://github.com/seeraven/powercounter)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""

# -----------------------------------------------------------------------------
# Module Imports
# -----------------------------------------------------------------------------
from typing import List, Optional, Union

# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------
ScalarFieldType = Union[bytes, bool, int]
OptionalScalarFieldType = Optional[ScalarFieldType]
FieldType = Union[OptionalScalarFieldType, List["FieldType"]]
