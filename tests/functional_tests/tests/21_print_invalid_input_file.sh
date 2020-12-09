#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the print subcommand with an invalid input file argument.
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
#   - Test the call without an invalid input file that has a return code of 1.
# -----------------------------------------------------------------------------
capture_output_failure call -i /dev/do_not_exists print


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
