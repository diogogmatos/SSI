#!/bin/bash

# Check if arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <executable_path> <executable_name>"
    exit 1
fi

# Extract the executable path and name from the arguments
executable_path=$1
executable_name=$2

# Create the systemd service file
# Create the systemd service file
sudo tee "/etc/systemd/system/$executable_name.service" > /dev/null <<EOF

[Unit]
Description=Custom service for $executable_name


[Service]
ExecStart=$HOME/2324-G10/TPs/TP2/bin/$executable_name
Restart=on-failure
User=mario
StartLimitInterval=0
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF


# Reload systemd daemon to pick up the changes
sudo systemctl daemon-reload

