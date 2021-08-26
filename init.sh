#!/usr/bin/env bash

# Fail fast
set -euo pipefail

WORK_DIR=$PWD


latest_release() {
    curl -s "https://api.github.com/repos/$1/releases/latest" |
    grep '"tag_name":' |
    sed -E 's/.*"v([^"]+)".*/\1/'
}


get_source() {
    echo "https://mediaarea.net/download/binary/mediainfo/$1/MediaInfo_CLI_$1_GNU_FromSource.tar.gz"
}


latest=$(latest_release "MediaArea/MediaInfo")
echo '
    _________________________________________
    |                                        |
    |    Building Binary for Mediainfo ...   |
    |________________________________________|
'
echo  "     Version :  v$latest"
echo  "     OS      :  Linux"
mkdir -p build && cd build
curl -s $(get_source $latest) | tar -xz
source_dir="MediaInfo_CLI_GNU_FromSource"
[ -d $source_dir ] && cd source_dir || exit 1
chmod +x CLI_Compile.sh && ./CLI_Compile.sh
