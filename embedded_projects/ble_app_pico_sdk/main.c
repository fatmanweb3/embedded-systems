#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"

int main()
{
    stdio_init_all();

    printf("Starting Pico 2 W...\n");

    if (cyw43_arch_init()) {
        printf("CYW43 initialization FAILED!\n");
        return -1;
    }

    printf("CYW43 initialized successfully.\n");
    printf("Blinking onboard LED...\n");

    while (1) {
        printf("LED ON\n");
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        sleep_ms(500);

        printf("LED OFF\n");
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        sleep_ms(500);
    }
}
