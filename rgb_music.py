import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
sys.excepthook = lambda *args: None
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import RPi.GPIO as GPIO
import threading
import time

# GPIO Setup
RED_PIN = 17
GREEN_PIN = 27
BLUE_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

red_pwm = GPIO.PWM(RED_PIN, 100)
green_pwm = GPIO.PWM(GREEN_PIN, 100)
blue_pwm = GPIO.PWM(BLUE_PIN, 100)
red_pwm.start(0)
green_pwm.start(0)
blue_pwm.start(0)

# Load the audio file (replace with your path)
AUDIO_FILE = "/home/pi/Music/Flight_of_the_Bumblebee.mp3"  # or .mp3 if ffmpeg is installed
song = AudioSegment.from_file(AUDIO_FILE)
samples = np.array(song.get_array_of_samples())
channels = song.channels
sample_rate = song.frame_rate

# Convert to mono
if channels == 2:
    samples = samples.reshape((-1, 2))
    samples = samples.mean(axis=1)

# Normalize to -1.0 to 1.0
max_abs = np.max(np.abs(samples))
if max_abs > 0:  # Avoid division by zero
    samples = samples / max_abs

chunk_size = 1024  # Adjust this for smoother/faster response
num_chunks = len(samples) // chunk_size
sleep_time = chunk_size / sample_rate  # Pre-calculate sleep time

def process_audio():
    for i in range(num_chunks):
        chunk = samples[i * chunk_size:(i + 1) * chunk_size]
        fft = np.fft.fft(chunk)
        fft = np.abs(fft[:len(fft) // 2])

        bass = np.mean(fft[0:80])
        mids = np.mean(fft[80:400])
        treble = np.mean(fft[400:1024])

        bass_val = min(100, bass / 5)
        mids_val = min(100, mids / 5)
        treble_val = min(100, treble / 5)

        red_pwm.ChangeDutyCycle(bass_val)
        green_pwm.ChangeDutyCycle(mids_val)
        blue_pwm.ChangeDutyCycle(treble_val)

        time.sleep(sleep_time)

def play_music():
    play(song)

try:
    print("Starting music and light show...")
    audio_thread = threading.Thread(target=process_audio)
    audio_thread.start()
    play_music()
    audio_thread.join()

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    try:
        red_pwm.ChangeDutyCycle(0)
        green_pwm.ChangeDutyCycle(0)
        blue_pwm.ChangeDutyCycle(0)

        red_pwm.stop()
        green_pwm.stop()
        blue_pwm.stop()
    except Exception as e:
        print("Error during PWM cleanup:", e)

    GPIO.cleanup()
    print("GPIO cleaned up successfully.")

