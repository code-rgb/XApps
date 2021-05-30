#!/bin/bash

# Install Requirements
pip install -U pip wheel setuptools
pip install --use-feature=in-tree-build .

# Run Python Script
python xapps/main.py


# Download apps from URLS
cat apk_urls.txt
while read url ;
do  
    pkg_name=$(basename $(echo $url) | xargs)
    if ! [[ $pkg_name == *.apk ]] ; then
        pkg_name="$pkg_name$RANDOM.apk"
    fi
    echo $pkg_name
    curl -sL -o $pkg_name $url
done < apk_urls.txt

# Compress Output
mkdir pakages && *.apk pakages/
tar -czvf pakages.tar.gz pakages
mkdir release && mv pakages.tar.gz "release/pakages.tar.gz"