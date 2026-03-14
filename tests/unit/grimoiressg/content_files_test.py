import pytest
from syrupy.assertion import SnapshotAssertion
from grimoiressg.content_files import deduplicate, expect_separator, split_frontmatter


def test_expected_separator_unknown():
    input = """!!!
    $birthday |= 1989-12-13
    !!!
    # Test Data
    more data!
    """

    separator = expect_separator(input)

    assert separator == None


def test_expected_separator_toml():
    input = """+++
    birthday = 1989-12-13
    +++
    # Test Data
    more data!
    """

    separator = expect_separator(input)

    assert separator == "+++\n"


def test_expected_separator_yaml():
    input = """---
    birthday: 1989-12-13
    ---
    # Test Data
    more data!
    """

    separator = expect_separator(input)

    assert separator == "---\n"


def test_split_frontmatter(snapshot: SnapshotAssertion) -> None:
    input = """---
    birthday: 1989-12-13
    ---
    # Test Data
    more data!
    """

    meta_data, content = split_frontmatter(input)

    assert meta_data.strip() == "birthday: 1989-12-13"
    assert content == snapshot


def test_split_frontmatter_no_frontmatter(snapshot) -> None:
    input = """# Test Data
    more data
    """

    meta_data, content = split_frontmatter(input)

    assert not meta_data
    assert content == snapshot


def test_deduplicate() -> None:
    deduplicated_list = deduplicate(
        [
            {"relative_filename": "State of Grace"},
            {"relative_filename": "Red"},
            {"relative_filename": "Treacherous"},
            {"relative_filename": "I Knew You Were Trouble"},
            {"relative_filename": "All Too Well"},
            {"relative_filename": "All Too Well"},
            {"relative_filename": "22"},
            {"relative_filename": "22"},
            {"relative_filename": "I Almost Do"},
            {"relative_filename": "We Are Never Ever Getting Back Together"},
            {"relative_filename": "Stay Stay Stay"},
            {"relative_filename": "The Last Time"},
            {"relative_filename": "Holy Ground"},
            {"relative_filename": "Sad Beautiful Tragic"},
            {"relative_filename": "The Lucky One"},
            {"relative_filename": "Everything Has Changed"},
            {"relative_filename": "Everything Has Changed"},
            {"relative_filename": "Starlight"},
            {"relative_filename": "Begin Again"},
        ]
    )

    assert len(deduplicated_list) == 16
