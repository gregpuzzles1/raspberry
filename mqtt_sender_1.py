import os
import time
import paho.mqtt.client as mqtt

# MQTT Broker IP (Change this to your Pi 5's actual IP)
BROKER = "10.0.0.229"
TOPIC = "pi5/cpu_temp"

# MQTT Client Setup
client = mqtt.Client("Pi5_Sender")

# MQTT Callback for Connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

client.on_connect = on_connect

# Attempt to connect to MQTT Broker
try:
    client.connect(BROKER)
    client.loop_start()  # Start non-blocking MQTT loop
except Exception as e:
    print(f"Connection error: {e}")
    exit(1)

# Function to get CPU temperature
def get_cpu_temp():
    """Read CPU temperature efficiently using vcgencmd."""
    try:
        # Using 'r' for read is more efficient than popen
        with os.popen("vcgencmd measure_temp") as temp_output:
            temp = temp_output.readline()
        return float(temp.replace("temp=", "").replace("'C\n", ""))
    except (ValueError, AttributeError) as e:
        print(f"Error reading temperature: {e}")
        return None

# Continuous publishing loop
while True:
    cpu_temp = get_cpu_temp()
    if cpu_temp is not None:
        try:
            client.publish(TOPIC, cpu_temp)
            print(f"Sent: CPU Temp {cpu_temp}°C")
        except Exception as e:
            print(f"Failed to publish: {e}")

    time.sleep(5)  # Send data every 5 seconds
