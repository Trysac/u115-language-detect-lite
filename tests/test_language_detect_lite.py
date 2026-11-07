"""Tests for language-detect-lite."""

from __future__ import annotations

import io
import pathlib
from unittest.mock import patch

import pytest

from language_detect_lite import LanguageError, detect, rank, train
from language_detect_lite.__main__ import main


def test_custom_train_acceptance() -> None:
    profiles = train({"xx": "aaa bbb aaa", "yy": "zzz qqq zzz"})
    assert detect("aaa aaa bbb bbb aaa", profiles=profiles, min_chars=5) == "xx"


def test_bundled_profiles_detection_first_batch() -> None:
    assert (
        detect("The weather is very nice today and we are going to the beach with our friends")
        == "en"
    )
    assert detect("El tiempo está muy bueno hoy y vamos a la playa con nuestros amigos") == "es"
    assert (
        detect("Das Wetter ist heute sehr schön und wir gehen mit unseren Freunden an den Strand")
        == "de"
    )


def test_bundled_profiles_detection_second_batch() -> None:
    assert detect("Il fait très beau aujourd hui et nous allons à la plage avec nos amis") == "fr"
    assert detect("O tempo está muito bom hoje e nós vamos à praia com os nossos amigos") == "pt"
    assert detect("Il tempo è molto bello oggi e andiamo al mare con i nostri amici") == "it"


def test_short_and_non_letter_inputs() -> None:
    assert detect("ok") is None
    assert detect("12345 !!! ...") is None
    assert detect("") is None


def test_rank_properties() -> None:
    text = "The weather is very nice today and we are going to the beach with our friends"
    res1 = rank(text)
    res2 = rank(text)

    # Repeated calls return identical results
    assert res1 == res2

    # Bundled languages: en, es, fr, de, pt, it (6 items)
    codes = [r[0] for r in res1]
    assert len(codes) == 6
    assert set(codes) == {"en", "es", "fr", "de", "pt", "it"}

    # Scores in [0.0, 1.0] and sorted descending by score, tie-breaking by code
    for i in range(len(res1)):
        code, score = res1[i]
        assert 0.0 <= score <= 1.0
        if i > 0:
            prev_code, prev_score = res1[i - 1]
            assert prev_score > score or (prev_score == score and prev_code < code)


def test_errors_and_limits() -> None:
    # Empty sample raises empty_sample
    with pytest.raises(LanguageError) as exc_info:
        train({"xx": ""})
    assert exc_info.value.code == "empty_sample"

    # Invalid code raises invalid_code
    with pytest.raises(LanguageError) as exc_info:
        train({"English": "abc"})
    assert exc_info.value.code == "invalid_code"

    # Text of 1_000_001 characters raises input_too_large
    huge_text = "a" * 1_000_001
    with pytest.raises(LanguageError) as exc_info:
        detect(huge_text)
    assert exc_info.value.code == "input_too_large"

    with pytest.raises(LanguageError) as exc_info:
        rank(huge_text)
    assert exc_info.value.code == "input_too_large"

    with pytest.raises(LanguageError) as exc_info:
        train({"xx": huge_text})
    assert exc_info.value.code == "input_too_large"

    # Invalid options
    with pytest.raises(LanguageError) as exc_info:
        train({"xx": "hello world"}, top=0)
    assert exc_info.value.code == "invalid_option"

    with pytest.raises(LanguageError) as exc_info:
        detect("hello", min_chars=-1)
    assert exc_info.value.code == "invalid_option"

    with pytest.raises(LanguageError) as exc_info:
        rank("hello", max_scan_chars=0)
    assert exc_info.value.code == "invalid_option"

    with pytest.raises(LanguageError) as exc_info:
        detect("hello", max_scan_chars=0)
    assert exc_info.value.code == "invalid_option"


def test_cli_acceptance(tmp_path: pathlib.Path) -> None:
    # main(['--rank', path]) prints one line per language formatted
    # '<code>\t<score with 4 decimals>' and returns 0
    p = tmp_path / "sample.txt"
    p.write_text(
        "The weather is very nice today and we are going to the beach with our friends",
        encoding="utf-8",
    )

    stdout_capture = io.StringIO()
    with patch("sys.stdout", stdout_capture):
        ret = main(["--rank", str(p)])
    assert ret == 0
    lines = stdout_capture.getvalue().strip().splitlines()
    assert len(lines) == 6
    for line in lines:
        parts = line.split("\t")
        assert len(parts) == 2
        code, score_str = parts
        assert len(code) in (2, 3)
        # Verify 4 decimals format
        float_val = float(score_str)
        assert 0.0 <= float_val <= 1.0
        assert len(score_str.split(".")[1]) == 4

    # main([path]) on a file with no letters prints 'und' and returns 1
    p_und = tmp_path / "und.txt"
    p_und.write_text("1234567890 !?@#$%^&*()", encoding="utf-8")
    stdout_capture_und = io.StringIO()
    with patch("sys.stdout", stdout_capture_und):
        ret_und = main([str(p_und)])
    assert ret_und == 1
    assert stdout_capture_und.getvalue().strip() == "und"


def test_cli_stdin_and_errors() -> None:
    # stdin detection
    with patch(
        "sys.stdin",
        io.StringIO(
            "The weather is very nice today and we are going to the beach with our friends"
        ),
    ):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            ret = main([])
        assert ret == 0
        assert stdout.getvalue().strip() == "en"

    # Non-existent file
    with patch("sys.stderr", io.StringIO()):
        ret_err = main(["/path/does/not/exist/998877.txt"])
    assert ret_err == 2

    # Help or bad arg
    with patch("sys.stderr", io.StringIO()):
        ret_arg = main(["--invalid-arg"])
    assert ret_arg == 2

    # LanguageError during execution
    with patch("sys.stdin", io.StringIO("a" * 1_000_001)):
        with patch("sys.stderr", io.StringIO()):
            ret_large = main([])
        assert ret_large == 2


def test_case_insensitivity_and_empty_profiles() -> None:
    lower_text = "the weather is very nice today and we are going to the beach with our friends"
    upper_text = lower_text.upper()
    assert detect(lower_text) == detect(upper_text)
    assert rank(lower_text) == rank(upper_text)

    # Empty profiles map
    assert rank("some text here", profiles={}) == []
    assert detect("some text here with enough chars", profiles={}) is None

    # Profile with non-alphabetic only raises empty_sample
    with pytest.raises(LanguageError) as exc_info:
        train({"xx": "12345 67890 !!!"})
    assert exc_info.value.code == "empty_sample"
