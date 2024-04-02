"""Configuration of pytest for functional tests."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import pytest


# ----------------------------------------------------------------------------
#  PYTEST ADDITIONAL OPTIONS
# ----------------------------------------------------------------------------
def pytest_addoption(parser):
    """Add options to the pytest argument parser."""
    parser.addoption(
        "--executable",
        action="store",
        type=str,
        help="The call of the powercounter app. Default: %(default)s",
        default="src/powercounter",
    )


@pytest.fixture(scope="session")
def executable(pytestconfig):
    """Fill the executable argument as a list of strings from the pytest option."""
    return pytestconfig.getoption("executable").split(" ")
