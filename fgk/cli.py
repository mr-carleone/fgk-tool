# fgk/cli.py

import sys
import os
from pathlib import Path
from loguru import logger
from .core import fgk_encode_bytes, fgk_decode_bits, bits_to_padded_bytes, padded_bytes_to_bits

# Настройка цветных логов
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)


def encode_file(input_path: str, output_path: str):
    logger.info(f"Encoding {input_path} -> {output_path}")
    with open(input_path, "rb") as f:
        data = f.read()

    bit_str = fgk_encode_bytes(data)
    encoded_bytes, padding = bits_to_padded_bytes(bit_str)

    with open(output_path, "wb") as f:
        f.write(bytes([padding]))  # 1 байт — сколько бит отбросить при декодировании
        f.write(encoded_bytes)

    orig_size = len(data)
    new_size = len(encoded_bytes) + 1
    ratio = new_size / orig_size if orig_size > 0 else 0
    logger.success(f"Encoded: {orig_size} B -> {new_size} B ({ratio:.1%})")


def decode_file(input_path: str, output_path: str):
    logger.info(f"Decoding {input_path} -> {output_path}")
    with open(input_path, "rb") as f:
        padding = f.read(1)[0]
        encoded_data = f.read()

    bit_str = padded_bytes_to_bits(encoded_data, padding)
    decoded = fgk_decode_bits(bit_str)

    with open(output_path, "wb") as f:
        f.write(decoded)

    logger.success("Decoding completed successfully")


def main():
    if len(sys.argv) != 4:
        logger.error("Usage: fgk encode <input> <output>  OR  fgk decode <input> <output>")
        sys.exit(1)

    command = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)

    try:
        if command == "encode":
            encode_file(input_file, output_file)
        elif command == "decode":
            decode_file(input_file, output_file)
        else:
            logger.error("Unknown command. Use 'encode' or 'decode'")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
