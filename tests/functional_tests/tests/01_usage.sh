#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the usage output.
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of powercounter (https://github.com/seeraven/powercounter)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


EXPECTED_OUTPUT_PREFIX=$(basename $0 .sh)
source $TEST_BASE_DIR/helpers/output_helpers.sh


# -----------------------------------------------------------------------------
# Tests:
#   - Test the usage output message with an return code of 0.
# -----------------------------------------------------------------------------
capture_output_success usage -h


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
