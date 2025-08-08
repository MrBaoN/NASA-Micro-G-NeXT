# TAMU_SA_NASA_MGN
Texas A&M University Sea Aggies - NASA Micro-g NExT Challange

# Usage

Start the Raspberry Pi. After ~2 minutes, connect to the Raspberry Pi's WiFi network "t-450" with password "tamug123". On a laptop, run the python script. This will provide a GUI showing what the Pi is recieving. On a phone, connect to the network and use a VNC client app like RVNC Viewer to connect to 10.42.0.1. This will bring up the same GUI, and provide an interface to control the Pi even with the closed box. Note that this can also be done on a laptop.

## Development

currently, starting the hotspot requires root password    

to make the MCP run on startup, I'll make a systemd service when it's closer to being ready

* install dependencies
  * sudo apt update && sudo apt upgrade
  * sudo apt -y install cmake g++ git libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev libboost-all-dev libgl1-mesa-dev python3-pyqt5 gnuradio wayvnc
  * sudo pip3 install --break-system-packages simplekml customtkinter
  * install it++ with these instructions: https://stackoverflow.com/questions/41077559/quick-and-hassle-free-installation-usage-of-it-library-on-linux-windows

Ensure port 5900 is open!

* If the wifi breaks, try these:
  * sudo rfkill unblock wifi && ip link set wlan0 up
  * sudo ifconfig wlan0 up
  * sudo nmcli radio wifi on

## Window manager

WayVNC requires us to use specific kind of window manager. I chose Hyprland. To make a new terminal, Windows-q. To close a window, Windows-C. To open a program, Windows-R and the name of the program. To change workspaces, Windows-num. To move the current window to a workspace, Windows-shift-num.
