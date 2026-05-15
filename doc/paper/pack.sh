#!/bin/bash

# Script to archive all relevant files from the doc/paper/ folder
# Includes: markdown files, tex files, bib files, Makefile, and planning/themes directories

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE_DIR="${SCRIPT_DIR}/../../"
ARCHIVE_NAME="kolmi-paper-$(date +%Y%m%d-%H%M%S).tar.gz"
ARCHIVE_PATH="${ARCHIVE_DIR}/${ARCHIVE_NAME}"

# Create a temporary directory for collecting files
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

# Create the paper directory structure in temp
mkdir -p "${TEMP_DIR}/kolmi-paper"

# Copy main directory files
echo "Archiving files from doc/paper/..."

# Copy all markdown files
find "${SCRIPT_DIR}" -maxdepth 1 -name "*.md" -exec cp {} "${TEMP_DIR}/kolmi-paper/" \;

# Copy tex files
find "${SCRIPT_DIR}" -maxdepth 1 -name "*.tex" -exec cp {} "${TEMP_DIR}/kolmi-paper/" \;

# Copy bibliography files
find "${SCRIPT_DIR}" -maxdepth 1 -name "*.bib" -exec cp {} "${TEMP_DIR}/kolmi-paper/" \;

# Copy Makefile
if [ -f "${SCRIPT_DIR}/Makefile" ]; then
    cp "${SCRIPT_DIR}/Makefile" "${TEMP_DIR}/kolmi-paper/"
fi

# Copy subdirectories (planning and themes)
for dir in planning themes; do
    if [ -d "${SCRIPT_DIR}/${dir}" ]; then
        cp -r "${SCRIPT_DIR}/${dir}" "${TEMP_DIR}/kolmi-paper/"
        echo "Included directory: ${dir}"
    fi
done

# Create the archive
echo "Creating archive: ${ARCHIVE_NAME}"
cd "${ARCHIVE_DIR}"
tar -czf "${ARCHIVE_NAME}" -C "${TEMP_DIR}" kolmi-paper/

echo "✓ Archive created successfully: ${ARCHIVE_PATH}"
echo "Archive size: $(du -h "${ARCHIVE_PATH}" | cut -f1)"

# Optional: List contents of archive
echo ""
echo "Archive contents:"
tar -tzf "${ARCHIVE_PATH}" | head -20
if [ $(tar -tzf "${ARCHIVE_PATH}" | wc -l) -gt 20 ]; then
    echo "... and more"
fi
