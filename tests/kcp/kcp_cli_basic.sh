#!/bin/bash
# Serves as a basic smoke test for KCP, ensuring that the compressor can run 
# end-to-end without errors on a simple input file. This test does not verify 
# compression ratios or output correctness, but it confirms that the main components 
# of KCP are functioning together as expected.
set -e

# Define paths
# Script lives in tests/kcp/, so go up three levels to repository root.
ROOT_DIR="$(dirname "$(dirname "$(dirname "$(realpath "$0")")")")"
KCP_PATH="$ROOT_DIR/kcp.py"
INPUT_FILE="$ROOT_DIR/tests/kcp/sample_input.txt"
OUTPUT_FILE="$ROOT_DIR/tests/kcp/sample_output.kcp"
# Create a sample input file if it doesn't exist
if [ ! -f "$INPUT_FILE" ]; then
    echo "This is a sample input file for KCP testing." > "$INPUT_FILE"
    echo "It contains multiple lines of text to simulate a realistic input." >> "$INPUT_FILE"
    echo "The purpose of this file is to serve as a test case for the KCP compressor." >> "$INPUT_FILE"
fi 

# Run KCP compression
echo "Running KCP compression on $INPUT_FILE..."
python3 "$KCP_PATH" compress "$INPUT_FILE" "$OUTPUT_FILE"
echo "KCP compression completed. Output file: $OUTPUT_FILE"

# Run decompression to verify it works without errors
DECOMPRESSED_FILE="$ROOT_DIR/tests/kcp/sample_decompressed.txt"
echo "Running KCP decompression on $OUTPUT_FILE..."
python3 "$KCP_PATH" decompress "$OUTPUT_FILE" "$DECOMPRESSED_FILE"
echo "KCP decompression completed. Decompressed file: $DECOMPRESSED_FILE"

# Verify checksum of original and decompressed files match (optional, can be removed if not needed)
ORIGINAL_CHECKSUM=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
DECOMPRESSED_CHECKSUM=$(sha256sum "$DECOMPRESSED_FILE" | awk '{print $1}')
if [ "$ORIGINAL_CHECKSUM" == "$DECOMPRESSED_CHECKSUM" ]; then
    echo "Checksum verification passed: Original and decompressed files match."
else
    echo "Checksum verification failed: Original and decompressed files do not match."
    exit 1
fi
