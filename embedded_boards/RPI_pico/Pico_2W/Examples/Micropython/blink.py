# from machine import Pin, Timer
# 
# led = Pin("LED", Pin.OUT)
# 
# tim = Timer()
# 
# def tick(timer):
#     global led
#     led.toggle()
# 
# 
# tim.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)



from machine import Pin
import time

led = Pin("LED", Pin.OUT)

while True:
    led.value(0)
    time.sleep(0.05)
    led.value(1)
    time.sleep(0.05)
