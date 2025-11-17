import RPi.GPIO as GPIO
import time
import random

# === GPIO Pin Setup ===
RED_PIN = 17
GREEN_PIN = 27
BLUE_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

# === PWM Setup (0–100% duty cycle) ===
red_pwm = GPIO.PWM(RED_PIN, 100)
green_pwm = GPIO.PWM(GREEN_PIN, 100)
blue_pwm = GPIO.PWM(BLUE_PIN, 100)

red_pwm.start(0)
green_pwm.start(0)
blue_pwm.start(0)

print("Cycling through RGB colors randomly at 5 times per second...")

try:
    while True:
        # Generate 3 random brightness levels (0–100%)
        r = random.randint(0, 100)
        g = random.randint(0, 100)
        b = random.randint(0, 100)

        red_pwm.ChangeDutyCycle(r)
        green_pwm.ChangeDutyCycle(g)
        blue_pwm.ChangeDutyCycle(b)

        time.sleep(0.2)  # 5 times per second

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    # Turn everything off
    red_pwm.ChangeDutyCycle(0)
    green_pwm.ChangeDutyCycle(0)
    blue_pwm.ChangeDutyCycle(0)

    red_pwm.stop()
    green_pwm.stop()
    blue_pwm.stop()

    GPIO.cleanup()
    print("GPIO cleaned up.")
