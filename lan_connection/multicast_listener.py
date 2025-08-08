import socket
import struct
import sys
import time
import platform
import tkinter as tk
import json
from threading import Thread

# This is to be run on the laptop only; DOES NOT WORK ON RBP

class MulticastListener:
    def __init__(self, root):
        self.root = root
        self.root.title("Multicast Listener")
        
        self.root.geometry("500x400")
        
        self.message_display = tk.Text(
            root,
            wrap=tk.WORD,
            bg="#f0f0f0",
            padx=10,
            pady=10,
            height=15,
            width=45
        )
        self.message_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.message_display.insert(tk.END, "Waiting for messages...")
        
        self.multicast_group = '224.1.1.1'
        self.port = 10000
        self.setup_socket()
        
        self.running = True
        self.thread = Thread(target=self.receive_loop)
        self.thread.daemon = True
        self.thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', self.port))
            
            group = socket.inet_aton(self.multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            ttl = struct.pack('b', 1)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            
            if platform.system() != 'Windows':
                try:
                    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b'wlan0')
                except:
                    print("Could not bind to wlan0 interface")
                    
            print(f"Listening for multicast messages on {self.multicast_group}:{self.port}...")
            
        except PermissionError:
            print("Permission error when binding to port. Try:")
            print("1. Run as administrator")
            print("2. Use a port number above 1024")
            print("3. Make sure no other application is using this port")
            sys.exit(1)
        except Exception as e:
            print(f"Socket setup error: {e}")
            sys.exit(1)
    
    def receive_loop(self):
        self.sock.settimeout(0.5)
        
        while self.running:
            try:
                data, address = self.sock.recvfrom(1024)
                message = data.decode()
                print(f"Received {len(data)} bytes from {address[0]}:{address[1]}")
                print(f"Data: {message}")
                
                # thread-safe way update
                self.root.after(0, self.update_message, message)
                
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Error in receive loop: {e}")
                time.sleep(1)
    
    def update_message(self, message):
        """Update the message display with new data (called from main thread)"""
        self.message_display.delete(1.0, tk.END)
        
        try:
            json_data = json.loads(message)
            formatted_json = json.dumps(json_data, indent=4)
            self.message_display.insert(tk.END, formatted_json)
        except json.JSONDecodeError:
            # Not valid JSON, just display as plain text
            self.message_display.insert(tk.END, message)
    
    def on_closing(self):
        """Handle window close event"""
        print("Shutting down listener...")
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(2.0)
        if hasattr(self, 'sock'):
            self.sock.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MulticastListener(root)
    root.mainloop()
    print("Program ended")