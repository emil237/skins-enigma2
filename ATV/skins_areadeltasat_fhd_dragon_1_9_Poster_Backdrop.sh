#!/bin/bash

echo "Removing previous version of skins_areadeltasat_fhd_dragon_1_9_Poster_Backdrop..."
sleep 2

# Check if the directory exists before removing it
if [ -d /usr/share/enigma2/AreaDeltasSat_FHD_Full ]; then
    rm -rf /usr/share/enigma2/AreaDeltasSat_FHD_Full > /dev/null 2>&1
    echo 'Package removed.'
else
    echo "You do not have previous version"
fi

echo ""
opkg install enigma2-plugin-extensions-bitrate enigma2-plugin-extensions-oaweather
opkg install curl
sleep 2

# Download and extract the package
cd /tmp || exit
curl -k -Lbk -m 55532 -m 555104 "https://github.com/emil237/skins-enigma2/raw/refs/heads/main/ATV/skins_areadeltasat_fhd_dragon_1_9_Poster_Backdrop.tar.gz" -o /tmp/skins_areadeltasat_fhd_dragon_1_9_Poster_Backdrop.tar.gz
sleep 1
echo "Installing ...."
tar -xzf /tmp/skins_areadeltasat_fhd_dragon_1_9_Poster_Backdrop.tar.gz -C /
echo ""
echo ""
sleep 1
rm -f /tmp/skins_areadeltasat_fhd_dragon_1_9_Poster_Backdrop.tar.gz
sleep 2
exit 0





