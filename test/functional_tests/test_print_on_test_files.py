"""Test the print output of the application on the test files from libsml-testing."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import subprocess
from pathlib import Path

# ----------------------------------------------------------------------------
#  LIBSML-TESTING DIRECTORY
# ----------------------------------------------------------------------------
LIBSML_TESTING_DIR = Path(__file__).parent.parent / "libsml-testing"


# ----------------------------------------------------------------------------
#  EXPECTED WARNINGS AND ERRORS
# ----------------------------------------------------------------------------
# Files where we expect a '[WARNING]: No message CRC provided!'
FILES_WITH_CRC_WARNINGS = [
    "DrNeuhaus_SMARTY_ix-130.bin",
    "EasyMeter_Q3A_A1064V1009.bin",
    "EMH-ED300L_consumption.bin",
    "EMH-ED300L_delivery.bin",
    "EMH_eHZ-HW8E2A5L0EK2P_1.bin",
    "EMH_eHZ-HW8E2A5L0EK2P_2.bin",
    "EMH_eHZ-HW8E2A5L0EK2P.bin",
    "EMH_eHZ-HW8E2AWL0EK2P.bin",
    "EMH_eHZ-IW8E2A5L0EK2P_with_error.bin",
    "EMH_eHZ-IW8E2AWL0EK2P.bin",
    "ISKRA_MT175_D1A52-V22-K0t.bin",
    "ISKRA_MT175_eHZ.bin",
]

# Files where we expect a '[ERROR]: Data for SmlRawMessageData must be of type list,
# but the given input type was <class 'bytes'>.'
FILED_WITH_MSG_TYPE_ERROR = [
    "DrNeuhaus_SMARTY_ix-130.bin",
    "DZG_DVS-7412.2_jmberg.bin",
    "DZG_DVS-7420.2V.G2_mtr0.bin",
    "DZG_DVS-7420.2V.G2_mtr1.bin",
    "DZG_DVS-7420.2V.G2_mtr2.bin",
    "DZG_DVS-7420.2V.G2_mtr2_neg.bin",
    "dzg_dwsb20_2th_2byte.bin",
    "dzg_dwsb20_2th_3byte.bin",
    "eBZ_DD3_DD32R06DTA-SMZ1.bin",
    "eBZ_DD3_DD3BZ06DTA-SMZ1_without_PIN.bin",
    "EMH-ED300L_consumption.bin",
    "EMH-ED300L_delivery.bin",
    "EMH_eHZ361L5R_1.bin",
    "EMH_eHZ361L5R.bin",
    "EMH_eHZ-GW8E2A500AK2.bin",
    "EMH_eHZ-HW8E2A5L0EK2P_1.bin",
    "EMH_eHZ-HW8E2A5L0EK2P_2.bin",
    "EMH_eHZ-HW8E2A5L0EK2P.bin",
    "EMH_eHZ-IW8E2AWL0EK2P.bin",
    "EMH_mME40-AE6AKF0K0.bin",
    "HOLLEY_DTZ541-ZDBA.bin",
    "ISKRA_MT631-D2A51-V22-K0z_without_PIN.bin",
    "ISKRA_MT691_eHZ-MS2020.bin",
    "ITRON_OpenWay-3.HZ.bin",
    "ITRON_OpenWay-3.HZ_without_PIN.bin",
    "ITRON_OpenWay-3.HZ_with_PIN.bin",
]

# Files where we expect a '[ERROR]: Expected end marker but found message start marker'
FILES_WITH_MARKER_ERRORS = ["DZG_DVS-7420.2V.G2_mtr1_error.bin"]

# Files where we expect a '[ERROR]: SML File has invalid CRC!'
FILES_WITH_SML_FILE_CRC_ERROR = ["dzg_dwsb20_2th_3byte.bin", "EasyMeter_Q3A_A1064V1009.bin"]


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_print_output_on_test_files(executable):
    """Test the output of the 'print' command using the test files of libsml-testing."""
    for test_file_path in LIBSML_TESTING_DIR.glob("*.bin"):
        result = subprocess.run(
            executable + ["-i", str(test_file_path), "print"],
            text=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert result.returncode == 0

        print(f"Checking {test_file_path}")
        if test_file_path.name in FILES_WITH_CRC_WARNINGS:
            assert "[WARNING]: No message CRC provided!" in result.stderr
        else:
            assert "[WARNING]: No message CRC provided!" not in result.stderr

        if test_file_path.name in FILED_WITH_MSG_TYPE_ERROR:
            assert (
                "[ERROR]: Data for SmlRawMessageData must be of type list, "
                "but the given input type was <class 'bytes'>." in result.stderr
            )
        else:
            assert (
                "[ERROR]: Data for SmlRawMessageData must be of type list, "
                "but the given input type was <class 'bytes'>." not in result.stderr
            )

        if test_file_path.name in FILES_WITH_MARKER_ERRORS:
            assert "[ERROR]: Expected end marker but found message start marker" in result.stderr
        else:
            assert "[ERROR]: Expected end marker but found message start marker" not in result.stderr

        if test_file_path.name in FILES_WITH_SML_FILE_CRC_ERROR:
            assert "[ERROR]: SML File has invalid CRC!" in result.stderr
        else:
            assert "[ERROR]: SML File has invalid CRC!" not in result.stderr
