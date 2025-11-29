# tests/test_fgk.py

import os
import sys
from loguru import logger
from fgk.core import fgk_encode_bytes, fgk_decode_bits

# Минимальная настройка логов только для тестов
logger.remove()
logger.add(
    sys.stderr,
    format="<level>{message}</level>",
    level="INFO"
)

def test_simple_string():
    text = "abracadabra"
    data = text.encode("utf-8")
    bits = fgk_encode_bytes(data)
    decoded = fgk_decode_bits(bits)
    assert decoded == data, f"Decoding mismatch"
    logger.info("✅ test_simple_string passed")


def test_file_roundtrip():
    import tempfile
    import sys
    test_content = b"Hello, FGK! This is a test with numbers: 12345 and symbols: @#$%^\n"

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(test_content)
        input_path = f.name

    encoded_path = input_path + ".fgk"
    decoded_path = input_path + ".decoded"

    try:
        from fgk.cli import encode_file, decode_file
        encode_file(input_path, encoded_path)
        decode_file(encoded_path, decoded_path)

        with open(decoded_path, "rb") as f:
            result = f.read()

        assert result == test_content, "File roundtrip failed"
        logger.info("✅ test_file_roundtrip passed")
    finally:
        # Cleanup
        for path in [input_path, encoded_path, decoded_path]:
            if os.path.exists(path):
                os.unlink(path)


if __name__ == "__main__":
    import sys
    # Подключим логгер
    logger.remove()
    logger.add(sys.stderr, format="<level>{message}</level>")

    test_simple_string()
    test_file_roundtrip()
    logger.info("🎉 All tests passed!")
