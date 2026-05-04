#!/bin/bash
REPO="Catafrancia123/cosub"
URL="https://github.com/${REPO}/archive/refs/tags/major.zip"
SUPPORTED_PYTHON_VERSIONS=("3.12" "3.13" "3.14")
OS=$(uname -s | tr '[:upper:]' '[:lower:]')

# check os
case "$OS" in
    linux|darwin) ;;
    mingw*|msys*|cygwin*) OS="windows" ;;
    *) printf "Unsupported OS: $OS" >&2; exit 1 ;;
esac

# get python version
if [ "$OS" = "linux" ]; then
    clear
    TMP=$(python3 --version 2>&1)
elif [ "$OS" = "windows" ]; then
    cls
    TMP=$(py --version 2>&1)
fi

PYTHON_VERSION=$(echo "$TMP" | sed -E 's/^Python ([0-9]+\.[0-9]+).*/\1/')

# check python version
found=
for v in "${SUPPORTED_PYTHON_VERSIONS[@]}"; do
    if [[ "$PYTHON_VERSION" == "$v" ]]; then
        found=1
        break
    fi
done

if [[ -z $found ]]; then
    echo "Unsupported Python version ($PYTHON_VERSION), please update to Python 3.12+"
    exit 1
fi

# download
FILE="cosub.zip"
printf "\nDownloading...\n\n"

if command -v curl > /dev/null; then
    curl -fSL -o "$FILE" "$URL"
elif command -v wget > /dev/null; then
    wget -qO "$FILE" "$URL"
else
    echo "Error: curl or wget required" >&2
    exit 1
fi
unzip "$FILE" -d COSUB

mv COSUB/cosub-major/* cosub/
rm -r COSUB/cosub-major
rm $FILE

printf "\n\nInstalled COSUB to the local directory.\n"
