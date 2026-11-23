import argparse
import subprocess
import sys


def capture_output(command, timeout):
    try:
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        return error.stdout or b"", error.stderr or b"", None

    return result.stdout, result.stderr, result.returncode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--qemu", required=True)
    parser.add_argument("--emulator", required=True)
    parser.add_argument("--firmware", required=True)
    parser.add_argument("--timeout", required=True, type=float)
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    qemu_command = [
        args.qemu,
        "-machine",
        "virt",
        "-m",
        "128M",
        "-bios",
        "none",
        "-kernel",
        args.firmware,
        "-display",
        "none",
        "-monitor",
        "none",
        "-serial",
        "stdio",
    ]
    emulator_command = [args.emulator, "--firmware", args.firmware]

    qemu_stdout, qemu_stderr, qemu_returncode = capture_output(
        qemu_command, args.timeout
    )
    emulator_stdout, emulator_stderr, emulator_returncode = capture_output(
        emulator_command, args.timeout
    )

    failed = False
    for name, stderr, returncode in (
        ("QEMU", qemu_stderr, qemu_returncode),
        ("rv32emu", emulator_stderr, emulator_returncode),
    ):
        if returncode not in (None, 0):
            failed = True
            print(f"{name} exited with status {returncode}", file=sys.stderr)
        if stderr:
            print(f"{name} stderr:\n{stderr.decode(errors='replace')}", file=sys.stderr)

    if qemu_stdout != emulator_stdout:
        failed = True
        print("Firmware output differs:", file=sys.stderr)
        print(f"QEMU: {qemu_stdout!r}", file=sys.stderr)
        print(f"rv32emu: {emulator_stdout!r}", file=sys.stderr)

    if failed:
        return 1

    print(f"Matched {len(qemu_stdout)} bytes of firmware output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
