#!/bin/bash
# Fail fast
set -euo pipefail

# Install Requirements
pip install -U pip wheel setuptools
pip install --use-feature=in-tree-build .

# Run Python Script
echo -e "Running python script\n"
python -m xapps
echo "SUCCESS"

# Download apps from URLS
while read url;
do  
    # Strip whitespaces
    pkg_name=$(basename $(echo $url) | xargs)
    # slice pakage name if it's longer than 40 char.
    if [[ "${#pkg_name}" -gt "40" ]] ; then
        pkg_name="${pkg_name:(-40)}"
    fi
    # check if it ends with ".apk"
    if ! [[ $pkg_name == *.apk ]] ; then
        pkg_name="$pkg_name$RANDOM.apk"
    fi
    echo $pkg_name
    curl -sL -o "$pkg_name" "$url"
done < apk_urls.txt

# Compress Output
mkdir -p pakages && mv *.apk pakages/
tar -czvf pakages.tar.gz pakages
mkdir release && mv pakages.tar.gz "release/pakages.tar.gz"
