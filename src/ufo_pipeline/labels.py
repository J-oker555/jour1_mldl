import re

import pandas as pd

HOAX_PATTERN = re.compile(r"\b(?:hoax|prank|fake|joke|joking|balloon prank)\b", re.IGNORECASE)


def build_hoax_label(comments: pd.Series) -> pd.Series:
    text = comments.fillna("").astype(str)
    return text.str.contains(HOAX_PATTERN, regex=True)
