from micropython import const
import utime as time
import framebuf
from machine import Pin, I2C

# SH1106 driver constants
_SET_CONTRAST        = const(0x81)
_SET_NORM_INV        = const(0xa6)
_SET_DISP            = const(0xae)
_SET_SCAN_DIR        = const(0xc0)
_SET_SEG_REMAP       = const(0xa0)
_LOW_COLUMN_ADDRESS  = const(0x00)
_HIGH_COLUMN_ADDRESS = const(0x10)
_SET_PAGE_ADDRESS    = const(0xB0)

class SH1106:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MVLSB)
        self.framebuf = fb
        self.fill = fb.fill
        self.fill_rect = fb.fill_rect
        self.hline = fb.hline
        self.vline = fb.vline
        self.line = fb.line
        self.rect = fb.rect
        self.pixel = fb.pixel
        self.scroll = fb.scroll
        self.text = fb.text
        self.blit = fb.blit
        self.init_display()

    def init_display(self):
        self.reset()
        self.fill(0)
        self.poweron()
        self.show()

    def poweroff(self):
        self.write_cmd(_SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(_SET_DISP | 0x01)

    def rotate(self, flag, update=True):
        if flag:
            self.write_cmd(_SET_SEG_REMAP | 0x01)
            self.write_cmd(_SET_SCAN_DIR | 0x08)
        else:
            self.write_cmd(_SET_SEG_REMAP | 0x00)
            self.write_cmd(_SET_SCAN_DIR | 0x00)
        if update:
            self.show()

    def sleep(self, value):
        self.write_cmd(_SET_DISP | (not value))

    def contrast(self, contrast):
        self.write_cmd(_SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(_SET_NORM_INV | (invert & 1))

    def show(self):
        for page in range(self.height // 8):
            self.write_cmd(_SET_PAGE_ADDRESS | page)
            self.write_cmd(_LOW_COLUMN_ADDRESS | 2)
            self.write_cmd(_HIGH_COLUMN_ADDRESS | 0)
            self.write_data(self.buffer[self.width * page:self.width * page + self.width])

    def reset(self, res):
        if res is not None:
            res(1)
            time.sleep_ms(1)
            res(0)
            time.sleep_ms(20)
            res(1)
            time.sleep_ms(20)

class SH1106_I2C(SH1106):
    def __init__(self, width, height, i2c, res=None, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.res = res
        self.temp = bytearray(2)
        if res is not None:
            res.init(res.OUT, value=1)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b'\x40'+buf)

    def reset(self):
        super().reset(self.res)

# Main program: Rotating 3D patterns
try:
    # I2C setup for Pico 2W (SDA=GP0, SCL=GP1)
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
    print("I2C devices found:", i2c.scan())  # Should show [60]
except Exception as e:
    print("I2C initialization error:", e)
    while True:
        pass

# Initialize OLED as 128x64 with SH1106
try:
    oled = SH1106_I2C(128, 64, i2c, addr=0x3C)
    print("Initialized OLED as 128x64 with SH1106")
except Exception as e:
    print("OLED initialization failed:", e)
    while True:
        pass

# Wake display, set contrast, clear, and show
oled.sleep(False)
oled.contrast(255)
oled.fill(0)
oled.show()
oled.invert(0)  # Normal display

# Animation loop
pattern = 0  # Current pattern (0: Cube, 1: Pyramid, 2: Sphere)
frame = 0  # Animation frame counter
x_position = 0  # Scrolling text position
direction = 1  # Scrolling direction
start_time = time.ticks_ms()

while True:
    try:
        oled.fill(0)  # Clear display

        # Switch patterns every 5 seconds
        if time.ticks_diff(time.ticks_ms(), start_time) > 5000:
            pattern = (pattern + 1) % 3
            frame = 0
            start_time = time.ticks_ms()

        # Pattern 1: Rotating Cube
        if pattern == 0:
            # Scrolling text
            oled.text("Rotating Cube", x_position, 0)
            # Calculate scale for back face (simulates rotation)
            scale = 16 + 8 * (1 + (frame % 20 - 10) / 10)  # Varies 8 to 24
            offset = (32 - scale) // 2
            # Front face (fixed square)
            oled.rect(40, 16, 32, 32, 1)
            # Back face (scales to simulate Y-axis rotation)
            oled.rect(40 + offset, 16 + offset, scale, scale, 1)
            # Connecting lines
            oled.line(40, 16, 40 + offset, 16 + offset, 1)  # Top-left
            oled.line(72, 16, 40 + offset + scale, 16 + offset, 1)  # Top-right
            oled.line(40, 48, 40 + offset, 16 + offset + scale, 1)  # Bottom-left
            oled.line(72, 48, 40 + offset + scale, 16 + offset + scale, 1)  # Bottom-right
            frame += 1

        # Pattern 2: Rotating Pyramid
        elif pattern == 1:
            oled.text("Rotating Pyramid", x_position, 0)
            # Base square
            oled.rect(30, 40, 40, 24, 1)
            # Apex shifts left/right for rotation effect
            apex_x = 50 + 10 * (frame % 20 - 10) // 10  # Shifts ±10 pixels
            oled.pixel(apex_x, 16, 1)
            # Connecting lines
            oled.line(30, 40, apex_x, 16, 1)  # Bottom-left to apex
            oled.line(70, 40, apex_x, 16, 1)  # Bottom-right to apex
            oled.line(30, 64, apex_x, 16, 1)  # Top-left to apex
            oled.line(70, 64, apex_x, 16, 1)  # Top-right to apex
            frame += 1

        # Pattern 3: Rotating Sphere
        else:
            oled.text("Rotating Sphere", x_position, 0)
            # Dithered circle with shifting pattern
            shift = frame % 4  # Shift dither every frame
            for y in range(16, 48):
                for x in range(40, 88):
                    if ((x - 64) ** 2 + (y - 32) ** 2) < 256:  # Radius ~16
                        if (x + y + shift) % 4 == 0:  # Rotating dither
                            oled.pixel(x, y, 1)
            frame += 1

        # Update scrolling text
        x_position += direction
        if x_position > 128:
            direction = -1
        elif x_position < -8 * len("Rotating Sphere"):  # Longest label
            direction = 1

        # Update display
        oled.show()

        # Animation speed (~20 fps)
        time.sleep(0.05)

    except Exception as e:
        print("Display update error:", e)
        time.sleep(1)