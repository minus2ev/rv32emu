# rv32emu

An RV32I system emulator targeting QEMU `virt` compatibility.

## Build and test

Requirements:
 - RISC-V cross-toolchain
 - RISC-V QEMU
 - python3

```sh
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

See top of root CMakeFiles.txt for options.