#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the capture subcommand with a missing output file argument.
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
#   - Test the call without an argument with an return code of 2.
# -----------------------------------------------------------------------------
capture_output 2 call capture


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
