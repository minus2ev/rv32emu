.section .text.init
.globl _start

_start:
    # Clear BSS
    la t0, __bss_start
    la t1, __bss_end

1:
    beq t0, t1, 2f
    sw zero, 0(t0)
    addi t0, t0, 4
    j 1b

2:
    # Initialize stack
    la sp, _stack_top

    # Enter C
    call main

3:
    j 3b
