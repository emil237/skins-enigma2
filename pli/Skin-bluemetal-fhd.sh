#!/bin/sh

echo "Starting skin installation..."
sleep 2

# 
cd /tmp

# 
curl -L --max-time 55532 "https://github.com/emil237/skins-enigma2/raw/refs/heads/main/pli/enigma2-plugin-skins-bluemetalfhd_v2.31_all.ipk" -o enigma2-plugin-skins-bluemetalfhd_v2.31_all.ipk

# 
if [ -f "enigma2-plugin-skins-bluemetalfhd_v2.31_all.ipk" ]; then
    echo "Installing the skin package..."
    opkg install --force-overwrite enigma2-plugin-skins-bluemetalfhd_v2.31_all.ipk

    # 
    if [ $? -eq 0 ]; then
        echo "Installation successful!"
    else
        echo "Installation failed!"
    fi
    # 
    rm -f enigma2-plugin-skins-bluemetalfhd_v2.31_all.ipk
else
    echo "Failed to download the skin package. Please check the URL or your internet connection."
fi

echo "Process completed."
exit



