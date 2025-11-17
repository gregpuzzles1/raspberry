import warnings
from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero import Device

# Force gpiozero to use RPi.GPIO
Device.pin_factory = RPiGPIOFactory()

# Optionally suppress fallback warnings
warnings.filterwarnings("ignore", category=UserWarning)
from gpiozero import RGBLED
from time import sleep
import random

# Define RGB LED pins
led = RGBLED(red=17, green=27, blue=22)

# List of colors (R, G, B)
colors = [
    (1, 0, 0),   # Red
    (0, 1, 0),   # Green
    (0, 0, 1),   # Blue
    (1, 1, 0),   # Yellow
    (0, 1, 1),   # Cyan
    (1, 0, 1),   # Magenta
    (1, 1, 1),   # White
]

try:
    while True:
        # Use random.choice instead of shuffling entire list
        color = random.choice(colors)
        led.color = color
        sleep(0.25)
        led.off()
        sleep(0.1)

except KeyboardInterrupt:
    led.off()
    print("\nRandom color cycle stopped by user.")

