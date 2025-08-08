import struct
import socket
import sys
import json
import time
import tkinter as tk
from tkinter import scrolledtext # For scrollable text area
from threading import Thread
import platform

class MulticasterApp:
    def __init__(self, root, fifo_path):
        self.root = root
        self.root.title("Multicaster")
        self.root.geometry("1280x720") # Same geometry as listener
        self.fifo_path = fifo_path

        self.message_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#f0f0f0", padx=10, pady=10, height=15, width=45)
        self.message_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.message_display.configure(font=("Liberation Mono", 50))
        self.message_display.configure(background='black', foreground='white')
        self.message_display.config(state=tk.DISABLED) # Make it read-only

        self.multicast_group = '224.1.1.1'
        self.multicast_port = 10000

        self.running = True
        self.sock = None
        
        self.update_display_area(f"Multicaster Initializing...\nFIFO Path: {self.fifo_path}\nAttempting to set up socket...")

        self.setup_socket() # This will also update the display

        if self.sock:
            self.update_display_area(f"Socket ready. Waiting for data from FIFO: {self.fifo_path}...")
            self.thread = Thread(target=self.read_fifo_loop)
            self.thread.daemon = True
            self.thread.start()
        else:
            self.update_display_area(f"ERROR: Failed to setup socket. Multicasting will not start.\nCheck console for errors.\nFIFO: {self.fifo_path}")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_display_area(self, message_content):
        """Clears the display and shows the new message_content."""
        def update_gui():
            self.message_display.config(state=tk.NORMAL)
            self.message_display.delete(1.0, tk.END) # Delete previous content
            self.message_display.insert(tk.END, message_content)
            self.message_display.config(state=tk.DISABLED)
        if self.root.winfo_exists(): # Check if root window still exists
            self.root.after(0, update_gui)

    def setup_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bound_to_device_message = "Using default interface for multicast."
            if platform.system() != 'Windows':
                try:
                    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b'wlan0')
                    bound_to_device_message = "Bound socket to wlan0 for multicast."
                except OSError as e:
                    # Log to console for more detail if needed
                    print(f"Console: Warning - Could not bind socket to wlan0: {e}. Using default interface.")
                    bound_to_device_message = f"Warning: Could not bind to wlan0 ({e}). Using default interface."
            else:
                bound_to_device_message = "SO_BINDTODEVICE not applicable on Windows. Using default interface."
            
            ttl = struct.pack('b', 1)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            # self.update_display_area(f"Socket setup complete.\n{bound_to_device_message}\nMulticasting to {self.multicast_group}:{self.multicast_port}")
            print(f"Console: Socket setup complete. {bound_to_device_message} Multicasting to {self.multicast_group}:{self.multicast_port}")


        except Exception as e:
            print(f"Console: Error setting up socket: {e}") # Log detailed error to console
            self.update_display_area(f"ERROR: Socket setup failed: {e}")
            self.sock = None

    def read_fifo_loop(self):
        if not self.sock:
            self.update_display_area("Socket not initialized. Cannot read FIFO or send multicast.")
            return

        # Initial message for FIFO reading state
        self.update_display_area(f"Attempting to open FIFO: {self.fifo_path}...")

        while self.running:
            display_message_on_loop_restart = f"Waiting for data from FIFO: {self.fifo_path}..."
            try:
                with open(self.fifo_path, 'r') as fifo:
                    if self.running:
                        self.update_display_area(f"Startup successful. Waiting for data...")
                        display_message_on_loop_restart = f"Waiting for data..."
                    while self.running:
                        data_line = fifo.readline()
                        if not self.running: break

                        if data_line:
                            stripped_data = data_line.strip()
                            current_display_content = ""
                            try:
                                received_dict = json.loads(stripped_data)
                                
                                countryCode = received_dict.get('countryCode')
                                longitude = received_dict.get('finalLong')
                                latitude = received_dict.get('finalLat')
                                hexId = received_dict.get('beconHexID')
                                timeStamp = received_dict.get('Time')
                                strLines = ""
                                strLines += f"Country Code: {countryCode}\n"

                                strLines += f"Hex ID: {hexId}\n"
                                strLines += f"Latitude: {latitude}\n"
                                strLines += f"Longitude: {longitude}\n"

                                strLines += f"Timestamp: {timeStamp} (UTC)\n"
                                
                                # formatted_json_for_display = json.dumps(received_dict, indent=4)
                                formatted_json_for_display = strLines

                                # Prepare data for sending (do this before updating display, in case sendto fails)
                                sent_data_encoded = json.dumps(received_dict).encode('utf-8')
                                sent_bytes = self.sock.sendto(sent_data_encoded, (self.multicast_group, self.multicast_port))

                                current_display_content = f"Last data sent:\n\n"
                                current_display_content += formatted_json_for_display
                                self.update_display_area(current_display_content)

                            except json.JSONDecodeError:
                                error_msg = f"Invalid JSON read from FIFO:\n'{stripped_data}'"
                                error_msg += "\n\nThis data was NOT sent."
                                self.update_display_area(error_msg)
                            except socket.error as se:
                                error_msg = f"Socket Error while sending data:\n{se}\n\nData that failed to send:\n{stripped_data}"
                                self.update_display_area(error_msg)
                            except Exception as e:
                                error_msg = f"Error processing/sending data:\n{e}\n\nData involved:\n{stripped_data}"
                                self.update_display_area(error_msg)
                            display_message_on_loop_restart = f"Last operation resulted in message above. Waiting for new data from FIFO: {self.fifo_path}..."


                        else: # Empty line from readline usually means EOF for regular files, or just a pause for FIFOs
                            time.sleep(0.1)
            except FileNotFoundError:
                if self.running:
                    self.update_display_area(f"FIFO '{self.fifo_path}' not found. Retrying in 5 seconds...")
                    time.sleep(5) # Give some time before retrying
            except Exception as e:
                if self.running:
                    self.update_display_area(f"Error reading from FIFO: {e}. Retrying in 5 seconds...")
                    time.sleep(5)
            
            if not self.running: break
            # If the loop restarts (e.g. after FIFO error and retry), show a waiting message
            self.update_display_area(display_message_on_loop_restart)


        if self.running: # If loop exited but still supposed to be running (should not happen with break)
            self.update_display_area("FIFO reading loop stopped unexpectedly.")
        # If self.running is false, on_closing will handle the final message

    def on_closing(self):
        if not self.running: # Already closing
            return
        self.update_display_area("Shutting down multicaster...")
        self.running = False
        time.sleep(0.1) # Give threads a moment to see self.running flag

        if hasattr(self, 'thread') and self.thread.is_alive():
            print("Console: Waiting for FIFO thread to join...")
            self.thread.join(1.0) # Reduced timeout
            if self.thread.is_alive():
                print("Console: FIFO thread did not join in time.")
        if self.sock:
            print("Console: Closing socket.")
            self.sock.close()
        
        # Final update before destroying, if window still exists
        if self.root.winfo_exists():
            self.update_display_area("Multicaster shutdown complete.")
            self.root.after(100, self.root.destroy) # Short delay before destroy
        else:
            print("Multicaster program ended (window closed).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <fifo_path>")
        if platform.system() != "Windows":
            fifo_path_default = "/tmp/my_multicast_fifo" # Example
            print(f"No FIFO path provided. For testing, you can create a FIFO (e.g., on Linux/macOS):\n  mkfifo {fifo_path_default}\nThen run: python {sys.argv[0]} {fifo_path_default}\nAnd write JSON strings to it: echo '{{\"test\":\"data\"}}' > {fifo_path_default}")
        sys.exit(1)

    fifo_path_arg = sys.argv[1]

    root = tk.Tk()
    root.attributes('-fullscreen', True)  # Fullscreen mode
    
    app = MulticasterApp(root, fifo_path_arg)
    root.mainloop()
    print("Multicaster program GUI closed.")