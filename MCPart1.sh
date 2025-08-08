# TAMU_SA_NASA_MGN\cpp_imgui\src\glad.c
# TAMU_SA_NASA_MGN\cpp_imgui\src\main.cpp
# TAMU_SA_NASA_MGN\cpp_imgui\src\stb.cpp
# TAMU_SA_NASA_MGN\KMLGen\KMLGenerator.py
# TAMU_SA_NASA_MGN\lan_connection\multicast_listener.py
# TAMU_SA_NASA_MGN\lan_connection\multicaster.py
# TAMU_SA_NASA_MGN\lan_connection\test1_broadcast.cpp
# TAMU_SA_NASA_MGN\lan_connection\test1_listener.py
# TAMU_SA_NASA_MGN\MicroGNextRaphael\code\bchdecode.cpp
# TAMU_SA_NASA_MGN\logFileFunction.cpp

# TAMU_SA_NASA_MGN\MCPart1.sh
#!/bin/bash

echo "==================================="
echo "  Running all programs concurrently"
echo "==================================="

# Create four named pipes
TCPtoPD===$(mktemp -u) 
PDtoBCH=$(mktemp -u)
BCHtoDDP=$(mktemp -u)
DDPtoLog=$(mktemp -u)

mkfifo "$TCPtoPD" "$PDtoBCH" "$BCHtoDDP" "$DDPtoLog"

# Attach them to file descriptors 3, 4, 5, and 6
exec 3<>"$TCPtoPD"
exec 4<>"$PDtoBCH"
exec 5<>"$BCHtoDDP"
exec 6<>"$DDPtoLog"

# Unlink the named pipes (they will persist until closed)
rm "$TCPtoPD" "$PDtoBCH" "$BCHtoDDP" "$DDPtoLog"

commands=(
    "./cpp_imgui/bin/glad"
    "./cpp_imgui/bin/main"
    "./cpp_imgui/bin/stb"
    "./lan_connection/bin/test1_broadcast"
    "./MicroGNextRaphael/bin/bchdecode <&4 >&5"  # Uses PDtoBCH (fd 4) as input and writes to BCHtoDDP (fd 5)
    "./MicroGNextRaphael/bin/debug_tcp >&3"  # Writes output to TCPtoPD (fd 3)
    "./bin/logFileFunction <&6"  # Reads from DDPtoLog (fd 6)
    "./packetDetector <&3 >&4"  # Reads from TCPtoPD (fd 3) and writes to PDtoBCH (fd 4)
    "./MicroGNextRaphael/bin/DDP <&5 >&6"  # Reads from BCHtoDDP (fd 5) and writes to DDPtoLog (fd 6)
    "./Logger <&6"  # Reads from DDPtoLog (fd 6)

    "python3 KMLGen/KMLGenerator.py"
    "python3 lan_connection/multicast_listener.py"
    "python3 lan_connection/multicaster.py"
    "python3 lan_connection/test1_listener.py"
)
pids=()

for cmd in "${commands[@]}"; do
    echo "Starting: $cmd"

    eval "$cmd &"
    pid=$!
    pids+=($pid)
    
    echo "Started with PID: $pid"
done

echo ""
echo "All programs have been launched in background."
echo "Process IDs: ${pids[@]}"

echo ""
echo "Waiting for all processes to complete..."
wait

echo ""
echo "All processes have completed. Script execution finished."