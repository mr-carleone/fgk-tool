# fgk/core.py

def fgk_encode_bytes(data: bytes) -> str:
    if not data:
        return ""

    NYT = -1
    nodes = []  # каждый узел: [symbol, left, right]
    symbol_to_leaf = {}  # symbol (int) -> node index

    def new_node(symbol, left=-1, right=-1):
        idx = len(nodes)
        nodes.append([symbol, left, right])
        return idx

    # Начинаем с одного NYT-листа — корень
    root_idx = new_node(NYT)

    def find_nyt_leaf():
        for i, (sym, l, r) in enumerate(nodes):
            if sym == NYT and l == -1 and r == -1:
                return i
        return -1

    def get_path(target_sym):
        """Возвращает битовую строку пути от корня до листа с target_sym"""
        from collections import deque
        queue = deque([(0, "")])  # (node_index, path)
        while queue:
            idx, path = queue.popleft()
            sym, left, right = nodes[idx]
            if sym == target_sym and left == -1 and right == -1:
                return path
            if left != -1:
                queue.append((left, path + "0"))
            if right != -1:
                queue.append((right, path + "1"))
        return ""

    output = []

    for byte in data:
        if byte in symbol_to_leaf:
            path = get_path(byte)
            output.append(path)
        else:
            nyt_path = get_path(NYT)
            output.append(nyt_path)
            output.append(format(byte, '08b'))

            nyt_idx = find_nyt_leaf()
            if nyt_idx == -1:
                raise RuntimeError("NYT leaf not found during encoding")

            # Заменяем NYT на внутренний узел
            char_leaf = new_node(byte)
            new_nyt = new_node(NYT)
            nodes[nyt_idx][0] = -2  # маркер внутреннего узла
            nodes[nyt_idx][1] = char_leaf
            nodes[nyt_idx][2] = new_nyt

            symbol_to_leaf[byte] = char_leaf

    return "".join(output)


def fgk_decode_bits(bit_str: str) -> bytes:
    if not bit_str:
        return b""

    NYT = -1
    nodes = []
    def new_node(symbol, left=-1, right=-1):
        idx = len(nodes)
        nodes.append([symbol, left, right])
        return idx

    root_idx = new_node(NYT)
    result = []
    i = 0

    while i < len(bit_str):
        idx = 0
        # Спускаемся, пока не дойдём до листа
        while nodes[idx][0] == -2:  # внутренний узел
            if i >= len(bit_str):
                raise ValueError("Incomplete bitstream during decoding")
            bit = bit_str[i]
            i += 1
            left, right = nodes[idx][1], nodes[idx][2]
            idx = left if bit == '0' else right

        sym = nodes[idx][0]

        if sym == NYT:
            if i + 8 > len(bit_str):
                raise ValueError("Truncated byte after NYT")
            byte_val = int(bit_str[i:i+8], 2)
            i += 8
            result.append(byte_val)

            # Расширяем дерево
            char_node = new_node(byte_val)
            nyt_node = new_node(NYT)
            nodes[idx][0] = -2
            nodes[idx][1] = char_node
            nodes[idx][2] = nyt_node
        else:
            result.append(sym)

    return bytes(result)


def bits_to_padded_bytes(bit_str: str):
    padding = (8 - len(bit_str) % 8) % 8
    padded = bit_str + "0" * padding
    byte_data = bytes(int(padded[i:i+8], 2) for i in range(0, len(padded), 8))
    return byte_data, padding


def padded_bytes_to_bits(data: bytes, padding: int) -> str:
    """Преобразует байты в битовую строку и удаляет padding битов в конце."""
    bits = "".join(f"{b:08b}" for b in data)
    if padding > 0:
        bits = bits[:-padding]
    return bits
