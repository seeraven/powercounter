"""Test the usage output of the application."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import subprocess


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_usage(executable):
    """Test the usage output when the '-h' or '--help' option is used."""
    assert "usage:" in subprocess.run(executable + ["--help"], text=True, check=False, stdout=subprocess.PIPE).stdout
    assert (
        "usage:"
        in subprocess.run(executable + ["capture", "--help"], text=True, check=False, stdout=subprocess.PIPE).stdout
    )
    assert (
        "usage:"
        in subprocess.run(executable + ["print", "--help"], text=True, check=False, stdout=subprocess.PIPE).stdout
    )
    assert (
        "usage:"
        in subprocess.run(executable + ["publish", "--help"], text=True, check=False, stdout=subprocess.PIPE).stdout
    )


def test_missing_subcommand(executable):
    """Test the output when using no subcommand."""
    result = subprocess.run(executable, text=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 2
    assert "Please specify a subcommand" in result.stderr


def test_capture_missing_arg(executable):
    """Test the output when using 'capture' command without an argument."""
    result = subprocess.run(
        executable + ["capture"], text=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert result.returncode == 2
    assert "error:" in result.stderr


def test_capture_invalid_device(executable):
    """Test the output when using 'capture' command with an invalid device."""
    result = subprocess.run(
        executable + ["-d", "/dev/does_not_exist", "capture", "/tmp/powercounter.raw"],
        text=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 1
    assert "[CRITICAL]: Can't open serial device" in result.stderr


def test_print_invalid_device(executable):
    """Test the output when using 'print' command with an invalid device."""
    result = subprocess.run(
        executable + ["-d", "/dev/does_not_exist", "print"],
        text=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 1
    assert "[CRITICAL]: Can't open serial device" in result.stderr


def test_print_invalid_input_file(executable):
    """Test the output when using 'print' command with an invalid input file."""
    result = subprocess.run(
        executable + ["-i", "/dev/does_not_exist", "print"],
        text=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 1
    assert "[CRITICAL]: Can't open input file" in result.stderr
