#!/bin/bash

# Install Requirements
pip install -U pip wheel setuptools
pip install .

# Run Python Script
python3 xapps/main.py

# Download apps from URLS
while read url ;
do  
    pkg_name=$(basename $url)
    if [[ pkg_name != *.apk ]] ; then
        pkg_name="$pkg_name.apk"
    fi
    curl -sL -o $pkg_name $url
done < apk_urls.txt

# Compress Output
ls *.apk
mkdir pakages && *.apk pakages/
tar -czvf pakages.tar.gz pakages
mkdir release && mv pakages.tar.gz "release/pakages.tar.gz"