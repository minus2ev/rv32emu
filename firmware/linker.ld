ENTRY(_start)

MEMORY
{
    RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 128M
}

SECTIONS
{
    . = ORIGIN(RAM);

    .text :
    {
        KEEP(*(.text.init))
        *(.text*)
    } > RAM

    .rodata :
    {
        *(.rodata*)
    } > RAM

    .data :
    {
        *(.data*)
    } > RAM

    . = ALIGN(4);

    __bss_start = .;

    .bss :
    {
        *(.bss*)
        *(COMMON)
    } > RAM

    __bss_end = .;

    . = ALIGN(16);
    _stack_top = ORIGIN(RAM) + LENGTH(RAM);
}
