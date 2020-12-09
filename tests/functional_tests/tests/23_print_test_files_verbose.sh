#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the print subcommand with the test file inputs and verbose output.
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
#   - Test the call with a valid input file.
# -----------------------------------------------------------------------------
for FILE in $TEST_BASE_DIR/../libsml-testing/*.bin; do
    BASENAME=$(basename $FILE .bin)
    capture_output_success $BASENAME -i $FILE print --verbose
done


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
