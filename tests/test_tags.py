"""Tag normalization should accept whatever humans write."""

from __future__ import annotations

import pytest

from clash_royale_api_py._tags import normalize_tag, tag_path_segment
from clash_royale_api_py.exceptions import InvalidTagError


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("2PP", "2PP"),
        ("#2PP", "2PP"),
        ("%232PP", "2PP"),
        (" 2pp ", "2PP"),
        ("# 2p p", "2PP"),
        ("0289PYLQGRJCUV", "0289PYLQGRJCUV"),
    ],
)
def test_normalize_tag(tag, expected):
    assert normalize_tag(tag) == expected


def test_path_segment_is_url_encoded():
    assert tag_path_segment("2PP") == "%232PP"
    assert tag_path_segment("#2PP") == "%232PP"


@pytest.mark.parametrize("tag", ["", "   ", "hello world!", "###", "xyz123"])
def test_invalid_tags_are_caught_early(tag):
    with pytest.raises(InvalidTagError):
        normalize_tag(tag)
