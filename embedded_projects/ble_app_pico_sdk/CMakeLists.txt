cmake_minimum_required(VERSION 3.13)

# Correctly targets the new RP2350-based Pico 2 W
set(PICO_BOARD pico2_w)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(led_blink C CXX ASM)

pico_sdk_init()

add_executable(led_blink
        main.c
        )

# Enable USB serial output so the board appears as a COM port / ttyACM
pico_enable_stdio_usb(led_blink 1)

# Disable hardware UART output (optional, but keeps things clean)
pico_enable_stdio_uart(led_blink 0)

target_link_libraries(led_blink
        pico_stdlib
        pico_cyw43_arch_none
        )

pico_add_extra_outputs(led_blink)
