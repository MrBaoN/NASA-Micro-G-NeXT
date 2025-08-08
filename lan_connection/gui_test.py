import socket
import struct
import sys
import time
import platform
import customtkinter as tk
from threading import Thread
import random

multicast_group = '224.1.1.1'
port = 10000

window = tk.CTk()
window.title("SDR Signal Receiver")
window.geometry("600x500")

# Create a scrollable frame for messages
scrollable_frame = tk.CTkScrollableFrame(window)
scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# List to keep track of message labels
message_labels = []

# Function to add message to GUI
def add_message(message):
    label = tk.CTkLabel(scrollable_frame, text=message, anchor="w", justify="left")
    label.pack(fill=tk.X, pady=5)
    
    # Add to our list of labels
    message_labels.append(label)
    
    # Auto-scroll to the bottom - ensure the newest message is visible
    scrollable_frame._parent_canvas.yview_moveto(1.0)

# Generate random SARSAT beacon data
def generate_sarsat_data():
    # Country codes (10 bits, bits 27-36)
    countries = ["USA", "CAN", "MEX", "BRA", "ARG", "FRA", "GBR", "DEU", "ITA", "ESP"]
    country = random.choice(countries)
    country_code = countries.index(country) + 200  # Just a random number between 200-210
    
    # Beacon Hex ID (bits 26-85)
    hex_id = hex(random.randint(0x1000000, 0xFFFFFFFF))[2:].upper()
    
    # Encoded Location (20 bits, bits 113-132)
    lat = random.uniform(-90, 90)
    lon = random.uniform(-180, 180)
    
    # Time received
    current_time = time.strftime('%H:%M:%S')
    
    return {
        "signal_type": random.choice(["121.65 MHz swept-tone", "406.025 MHz SARSAT"]),
        "country_code": f"{country} ({country_code})",
        "hex_id": hex_id,
        "location": f"Lat: {lat:.5f}, Lon: {lon:.5f}",
        "time": current_time
    }

# Simulate receiving data
def simulate_messages():
    while True:
        # Generate random beacon data
        data = generate_sarsat_data()
        
        # Format message based on signal type
        if data["signal_type"] == "121.65 MHz swept-tone":
            message = f"recieved 121.65 signal\n" \
                     f"Time: {data['time']}\n" \
                     f"Signal Strength: {random.randint(5, 95)}%"
        else:
            message = f"recieved 406.025 signal\n" \
                     f"Time: {data['time']}\n" \
                     f"Country Code: {data['country_code']}\n" \
                     f"Beacon Hex ID: {data['hex_id']}\n" \
                     f"Encoded Location: {data['location']}"
        
        # Update GUI from main thread
        window.after(0, add_message, message)
        
        # Wait some time before sending next message
        time.sleep(random.uniform(3, 8))

# Start simulation in a separate thread
simulation_thread = Thread(target=simulate_messages, daemon=True)
simulation_thread.start()

# Add buttons frame
button_frame = tk.CTkFrame(window)
button_frame.pack(fill=tk.X, padx=10, pady=5)

# Add a button to manually trigger a 121.65 MHz signal detection
def add_swept_tone():
    data = generate_sarsat_data()
    data["signal_type"] = "121.65 MHz swept-tone"
    message = f"[MANUAL DETECT] 121.65 MHz swept-tone signal\n" \
              f"Time: {data['time']}\n" \
              f"Signal Strength: {random.randint(5, 95)}%"
    add_message(message)

# Add a button to manually trigger a 406.025 MHz signal detection
def add_sarsat():
    data = generate_sarsat_data()
    data["signal_type"] = "406.025 MHz SARSAT"
    message = f"[MANUAL DETECT] 406.025 MHz SARSAT signal\n" \
              f"Time: {data['time']}\n" \
              f"Country Code: {data['country_code']}\n" \
              f"Beacon Hex ID: {data['hex_id']}\n" \
              f"Encoded Location: {data['location']}"
    add_message(message)

# Clear messages button
def clear_messages():
    for label in message_labels:
        label.destroy()
    message_labels.clear()

clear_button = tk.CTkButton(button_frame, text="Clear Messages", command=clear_messages)
clear_button.pack(side=tk.LEFT, padx=5, pady=5)

# Add status bar
status_bar = tk.CTkLabel(window, text="SDR Status: Active | Antenna: Connected", anchor="w")
status_bar.pack(fill=tk.X, padx=10, pady=5)

# Start the main loop
print("SDR Simulation Mode: Generating random signal detections")
window.mainloop()
print("GUI closed")