#include <stdint.h>

#define UART_BASE 0x10000000u

#define UART_THR (*(volatile uint8_t *)(UART_BASE + 0))
#define UART_LSR (*(volatile uint8_t *)(UART_BASE + 5))

#define UART_LSR_THRE (1u << 5)

static void uart_putc(char c)
{
    while ((UART_LSR & UART_LSR_THRE) == 0)
        ;

    UART_THR = (uint8_t)c;
}

static void uart_puts(const char *s)
{
    while (*s)
        uart_putc(*s++);
}

int main(void)
{
    uart_puts("Hello from bare-metal RV32!\r\n");
    return 0;
}
