#!/usr/bin/bash

# Check if there is no install location
if [$1 = ""]; then
    echo Please provide a install location. Ex: /usr/local/bin/
    exit 1
fi

# Install packages from pip
pip3 install colorama
pip3 install requests

echo Depending on where you install, the builder might ask for sudo permissions.

# Remove old version of RIFT
sudo rm $1

# Move rift to /usr/local/bin
sudo cp rift.py $1/rift
sudo chmod +x$1/rift

# Run
rift