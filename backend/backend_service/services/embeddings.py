from __future__ import annotations

import hashlib
import struct
from typing import List


def deterministic_embedding(text: str) -> List[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    parts = struct.unpack("!8I", digest[:32])
    scale = float(2**32)
    return [round(value / scale, 6) for value in parts]
