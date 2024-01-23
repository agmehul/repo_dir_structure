#!/bin/bash

# Take EDP_DIR as input from command line
EDP_DIR="$1"

# Check if EDP_DIR is provided
if [ -z "$EDP_DIR" ]; then
    echo "Usage: $0 <EDP_DIR>"
    exit 1
fi

# Set installables directory
INSTALLABLES_DIR="$EDP_DIR/installables"

# Step 5.1: Extract Trino Protector package
mkdir -p "$EDP_DIR/starhurst/dbprotector"
tar xvf "$INSTALLABLES_DIR/DatabaseProtector_Linux_ALL-64_x86-64_Trino-407-64_7.2.tar.gz" -C "$EDP_DIR/starhurst/dbprotector"

# Step 5.2: Update Trino config file
touch "$EDP_DIR/starburst/diprotector/bost"
CONFIG_FILE="$EDP_DIR/starburst/diprotector/Trisu.config"

# Modify Trino.config parameters
sed -i "s|THINO PLUGIN DIB.*|THINO PLUGIN DIB $EDP_DIR/starburat/mprotector|" "$CONFIG_FILE"
sed -i "s|PROTEORITY DIR.*|PROTEORITY DIR $EDP_DIR/starburst/protegrity|" "$CONFIG_FILE"
sed -i "s|CLUSTERLIST FILER.*|CLUSTERLIST FILER /bests|" "$CONFIG_FILE"
sed -i "s|AUTOCREATE PROTEORITY IT USPO.*|AUTOCREATE PROTEORITY IT USPO $1|" "$CONFIG_FILE"
sed -i "s|PROTEGRITY IT USR GROUP.*|PROTEGRITY IT USR GROUP $2|" "$CONFIG_FILE"

# Step 5.3: Install Trino Protector
cd "$EDP_DIR/<Trino Protector package extraction directory>/"
./TrinoProtectorInstal1407 Linux-ALL 7.2.1.7-trino.sh

# Prompt to confirm Trino Protector installation
read -p "Do you want to continue with the Trino Protector installation? (yes/no): " INSTALL_CONFIRM
if [ "$INSTALL_CONFIRM" == "yes" ]; then
    # Prompt for PEP server information
    read -p "Is the PEP server already installed? (yes/no): " PEP_INSTALLED
    if [ "$PEP_INSTALLED" == "no" ]; then
        read -p "Enter ESA IP: " ESA_IP
        read -p "Enter user with permissions to download certificates: " CERT_USER
        # Additional steps for certificate download can be added here
    fi

    # Restart Trino server
    echo "Restarting Trino server..."
    # Add command to restart Trino server

else
    echo "Trino Protector installation cancelled."
fi
