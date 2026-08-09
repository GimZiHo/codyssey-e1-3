"""Convert external label aliases into internal standard labels."""

from mini_npu.constants import CROSS, X_LABEL


LABEL_ALIASES = {
    "+": CROSS,
    "cross": CROSS,
    "x": X_LABEL,
}


def normalize_label(value: str) -> str:
    """Return the standard Cross/X label for a supported external value."""
    if not isinstance(value, str):
        raise ValueError("label must be a string.")

    normalized_key = value.strip().lower()
    if normalized_key not in LABEL_ALIASES:
        raise ValueError("unsupported label: {!r}.".format(value))

    return LABEL_ALIASES[normalized_key]
