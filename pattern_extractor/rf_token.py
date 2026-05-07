from __future__ import annotations

from collections import Counter

import tiktoken

RF_TOKEN_VERSION = "v1_token_overlap_cl100k"
TOKENIZER_VERSION = "cl100k_base"
encoding = tiktoken.get_encoding("cl100k_base")


def compute_rf_token_v1(curr_text, prev_text, encoding_obj) -> float:
    tokens_curr = encoding_obj.encode(curr_text)
    tokens_prev = encoding_obj.encode(prev_text)

    if len(tokens_curr) == 0:
        return 0.0

    if len(tokens_prev) == 0:
        return 0.0

    count_curr = Counter(tokens_curr)
    count_prev = Counter(tokens_prev)

    overlap = sum(min(count_curr[token], count_prev.get(token, 0)) for token in count_curr)
    rf = overlap / len(tokens_curr)
    return round(rf, 6)


def safe_compute_rf_token_v1(curr_text, prev_text, encoding_obj=encoding):
    try:
        rf = compute_rf_token_v1(curr_text, prev_text, encoding_obj)
    except Exception:
        return None, True

    return rf, False
