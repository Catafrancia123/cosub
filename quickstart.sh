#/bin/bash
REPO="Catafrancia123/cosub"
URL="https://github.com/${REPO}/archive/refs/tags/major.zip"
SUPPORTED_PYTHON_VERSIONS=("3.12", "3.13", "3.14")
OS=$(uname -s | tr '[:upper:]' '[:lower:]')

# check os
case "$OS" in
    linux|darwin) ;;
    mingw*|msys*|cygwin*) OS="windows" ;;
    *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac

if [ "$OS" = "linux" ]; then
	sudo apt update && sudo apt upgrade python3
	TMP=$(python3 --version)
elif [ "$OS" = "windows" ]; then
	TMP=$(py --version)
PYTHON_VERSION=$(echo $TMP | sed -E 's/^Python ([0-9]+\.[0-9]+?).*/\1/')

# check python version
for i in {1..3} do
	if [ "$PYTHON_VERSION" = "${SUPPORTED_PYTHON_VERSIONS[i]}" ]; then
		break
	else
		echo "Unsupported Python version, please update to Python 3.12+"; exit 1
	fi
done

# download
echo "Downloading..."

if command -v curl > /dev/null; then
    curl -fSL -o "./" "$URL"
elif command -v wget > /dev/null; then
    wget -qO "./" "$URL"
else
    echo "Error: curl or wget required" >&2; exit 1
fi

