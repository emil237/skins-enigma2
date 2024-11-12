#!/bin/sh

echo "Starting skin installation..."
sleep 2

# 
cd /tmp || { echo "Failed to access /tmp directory."; exit 1; }

# 
curl -L --max-time 55532 "https://github.com/emil237/skins-enigma2/raw/refs/heads/main/pli/enigma2-plugin-skins-bardo-fhd_V-3.7.2_by_Martina3-Mod_by-Biko_all.ipk" -o enigma2-plugin-skins-bardo-fhd_V-3.7.2_by_Martina3-Mod_by-Biko_all.ipk

# 
if [ -f "enigma2-plugin-skins-bardo-fhd_V-3.7.2_by_Martina3-Mod_by-Biko_all.ipk" ]; then
    echo "Installing the skin package..."

# 
    if opkg install --force-overwrite enigma2-plugin-skins-bardo-fhd_V-3.7.2_by_Martina3-Mod_by-Biko_all.ipk; then
        echo "Installation successful!"
    else
        echo "Installation failed!"
        exit 1
    fi

# 
    rm -f enigma2-plugin-skins-bardo-fhd_V-3.7.2_by_Martina3-Mod_by-Biko_all.ipk
else
    echo "Failed to download the skin package. Please check the URL or your internet connection."
    exit 1
fi

echo "Process completed."
exit 0



