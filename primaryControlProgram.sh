#!/bin/bash

sleep 1
DISPLAY=:0

# DO NOT RUN WITH SUDO

# rm -r fifos -Y
echo "Creating fifos..."
mkdir bin
mkdir fifos
mkdir kmls
TCPtoPD="fifos/tcpTOpd"
PDtoBCH="fifos/pdTObch"
DECODERtoTCP="fifos/decoder_fifo"
toMULTICAST="fifos/bchTOcast" # 
toKML="fifos/bchTOkml"
mkfifo "$TCPtoPD" "$PDtoBCH" "$toMULTICAST" "$toKML" "$DECODERtoTCP"

# compile cpp progams
declare -A compileCMD=( ["bchdecode"]="g++ -o bin/bchdecode MicroGNextRaphael/code/bchdecode.cpp -litpp -lzmq"                         )

declare -A cppFileArg=( ["bchdecode"]="$PDtoBCH $toMULTICAST $toKML" # bchdecode translates recieved packets and sends/records them
                        )

declare -A pyFileArg=(  ["MicroGNextRaphael/launcher.py"]="$"
                        ["KMLGen/KMLGenerator.py"]="$toKML" # KMLGen records the packets locally
                        ["lan_connection/multicaster.py"]="$toMULTICAST" # sends the packets over LAN
                        )
                        
declare -A pidArray=() # key is PID, value is filename

echo Setting up Wi-Fi...
nmcli device wifi hotspot con-name tamug ssid t-450 band bg password tamug123 > echo
echo done

echo Initiating VNC. Please connect to 10.42.0.1
wayvnc 0.0.0.0 &

cleanup() {
    trap - EXIT
    echo "Terminating programs..."
    for pid in ${!pidArray[@]}; do
        fileName="${pidArray[$pid]}"
        echo "Killing $fileName - $pid"

        if kill "$pid" 2>/dev/null; then
            wait "$pid" 2>/dev/null
        fi
        unset pidArray[$pid]
    done

    echo Killing VNC...
    killall wayvnc

    echo Removing Wi-Fi...
    nmcli connection delete tamug
    echo done
    
    rm -r bin
    exit 0
}

trap cleanup EXIT

restart() {
    fileName="${pidArray[$1]}"

    if kill $1 2>/dev/null; then
        wait $1 2>/dev/null
    fi
    unset pidArray[$1]

    if [[ -v pyFileArg["$fileName"] ]]; then
        (trap - EXIT; python3 "$fileName" ${pyFileArg["$fileName"]})&
    else
        ( trap - EXIT; ./bin/"$fileName" ${cppFileArg["$fileName"]} )& 
    fi
    newPID=$!
    pidArray[$newPID]="$fileName"
    echo "Restarted $fileName - $1 with new process $newPID"
    # restart the correct file
}

for file in ${!compileCMD[@]}; do
    echo "Compiling $file"
    ${compileCMD["$file"]}
done

for file in "${!pyFileArg[@]}"; do
    echo "Executing "$file" and binding fifos..."
    # Execute the compile command stored in the array
    ( trap - EXIT; python3 "$file" ${pyFileArg["$file"]} )& 
    pid=$!                  
    pidArray[$pid]="$file"   
done

for file in "${!cppFileArg[@]}"; do
    echo "Executing "$file" and binding fifos..."
    # Execute the compile command stored in the array
    ( trap - EXIT; ./bin/"$file" ${cppFileArg["$file"]} )& 
    pid=$!                  
    pidArray[$pid]="$file"   
done

while true; do
    read -t 1 -n 1 input
    if [[ $input == "q" ]]; then
        cleanup 
        break
    fi
    # If the process is not running, call restart()
    for pid in ${!pidArray[@]}; do
        if ! ps -p $pid > /dev/null 2>&1; then
            restart $pid
        fi
    done
done
