cmake_minimum_required(VERSION 3.20)

project(rv32emu LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build and test settings. Edit these values to control the generated targets.
set(BUILD_TESTING ON)
set(RV32EMU_BUILD_INTEGRATION_TESTS OFF)
set(RV32EMU_INTEGRATION_CAPTURE_TIMEOUT 5)
set(RV32_FIRMWARE_GCC "riscv32-unknown-elf-gcc")
set(RV32EMU_QEMU "qemu-system-riscv32")

include(CTest)

add_library(rv32emu_lib
    src/elf_parser.cpp
)
target_include_directories(rv32emu_lib
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

add_executable(rv32emu
    src/main.cpp
)
target_link_libraries(rv32emu
    PRIVATE
        rv32emu_lib
)

find_program(RV32_FIRMWARE_GCC_EXECUTABLE NAMES "${RV32_FIRMWARE_GCC}")
if(RV32_FIRMWARE_GCC_EXECUTABLE)
    set(RV32_FIRMWARE_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/firmware")
    set(RV32_FIRMWARE_ELF "${RV32_FIRMWARE_OUTPUT_DIR}/hello.elf")
    set(RV32_FIRMWARE_MAP "${RV32_FIRMWARE_OUTPUT_DIR}/hello.map")

    set(RV32_FIRMWARE_CFLAGS
        -march=rv32i
        -mabi=ilp32
        -mcmodel=medany
        -msmall-data-limit=0
        -mno-relax
        -ffreestanding
        -fno-builtin
        -fno-stack-protector
        -fno-pie
        -O2
        -Wall
        -Wextra
    )

    add_custom_command(
        OUTPUT "${RV32_FIRMWARE_ELF}"
        BYPRODUCTS "${RV32_FIRMWARE_MAP}"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${RV32_FIRMWARE_OUTPUT_DIR}"
        COMMAND "${RV32_FIRMWARE_GCC_EXECUTABLE}" ${RV32_FIRMWARE_CFLAGS}
            -nostdlib
            -nostartfiles
            -no-pie
            "-Wl,-T,${CMAKE_CURRENT_SOURCE_DIR}/firmware/linker.ld"
            "-Wl,-Map,${RV32_FIRMWARE_MAP}"
            -Wl,--build-id=none
            -Wl,--no-relax
            "${CMAKE_CURRENT_SOURCE_DIR}/firmware/start.S"
            "${CMAKE_CURRENT_SOURCE_DIR}/firmware/main.c"
            -o "${RV32_FIRMWARE_ELF}"
        DEPENDS
            firmware/main.c
            firmware/start.S
            firmware/linker.ld
        VERBATIM
        COMMENT "Building RV32I QEMU virt firmware"
    )

    add_custom_target(firmware ALL DEPENDS "${RV32_FIRMWARE_ELF}")
else()
    message(STATUS
        "Firmware target unavailable: ${RV32_FIRMWARE_GCC} was not found"
    )
endif()

if(BUILD_TESTING)
    include(FetchContent)

    set(CATCH_BUILD_TESTING OFF CACHE BOOL "" FORCE)
    set(CATCH_INSTALL_DOCS OFF CACHE BOOL "" FORCE)
    set(CATCH_INSTALL_HELPERS OFF CACHE BOOL "" FORCE)

    FetchContent_Declare(
        Catch2
        GIT_REPOSITORY https://github.com/catchorg/Catch2.git
        GIT_TAG v3.8.1
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(Catch2)

    add_executable(rv32emu_tests tests/elf_parser_tests.cpp)
    target_link_libraries(rv32emu_tests
        PRIVATE
            rv32emu_lib
            Catch2::Catch2WithMain
    )

    add_test(NAME rv32emu_tests COMMAND rv32emu_tests)
    set_tests_properties(rv32emu_tests PROPERTIES LABELS unit)
endif()

if(RV32EMU_BUILD_INTEGRATION_TESTS)
    if(NOT BUILD_TESTING)
        message(FATAL_ERROR
            "RV32EMU_BUILD_INTEGRATION_TESTS requires BUILD_TESTING=ON"
        )
    endif()
    if(NOT TARGET firmware)
        message(FATAL_ERROR
            "Integration tests require riscv32-unknown-elf-gcc to build firmware"
        )
    endif()

    find_package(Python3 3.8 COMPONENTS Interpreter REQUIRED)
    find_program(RV32EMU_QEMU_EXECUTABLE NAMES "${RV32EMU_QEMU}" REQUIRED)

    add_test(
        NAME rv32emu_firmware_output
        COMMAND
            "${Python3_EXECUTABLE}"
            "${CMAKE_CURRENT_SOURCE_DIR}/tests/integration/compare_firmware_output.py"
            --qemu "${RV32EMU_QEMU_EXECUTABLE}"
            --emulator "$<TARGET_FILE:rv32emu>"
            --firmware "${RV32_FIRMWARE_ELF}"
            --timeout "${RV32EMU_INTEGRATION_CAPTURE_TIMEOUT}"
    )
    set_tests_properties(rv32emu_firmware_output PROPERTIES
        LABELS integration
        TIMEOUT 15
    )
endif()
