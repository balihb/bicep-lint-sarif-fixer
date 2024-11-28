import json
from io import StringIO
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from bicep_lint_sarif_fixer import (
    add_rules_to_sarif_dict,
    process_sarif_string,
    process_sarif_file,
)


@pytest.fixture
def sample_sarif():
    """Provide a sample SARIF data structure for testing."""
    return {
        "runs": [
            {
                "results": [
                    {"ruleId": "adminusername-should-not-be-literal"},
                    {"ruleId": "artifacts-parameters"},
                    {"ruleId": "unknown-rule"},
                ],
                "tool": {"driver": {}},
            }
        ]
    }


@pytest.fixture
def expected_rules():
    """Provide the expected rules to be added to the SARIF data."""
    return [
        {
            "id": "adminusername-should-not-be-literal",
            "name": "Admin user name not literal",
            "shortDescription": {"text": "Property 'adminUserName' should not use a literal value. Use a param instead."},
            "helpUri": "https://aka.ms/bicep/linter/adminusername-should-not-be-literal",
            "properties": {"category": "Security"},
            "defaultConfiguration": {"level": "warning"},
        },
        {
            "id": "artifacts-parameters",
            "name": "Artifacts parameters",
            "shortDescription": {"text": "Follow best practices when including the _artifactsLocation and _artifactsLocationSasToken parameters."},
            "helpUri": "https://aka.ms/bicep/linter/artifacts-parameters",
            "properties": {"category": "BestPractice"},
            "defaultConfiguration": {"level": "warning"},
        },
    ]


def test_add_rules_to_sarif_dict(sample_sarif, expected_rules):
    """Test that rules are correctly added to SARIF data."""
    updated_sarif = add_rules_to_sarif_dict(sample_sarif)

    # Verify that the "rules" section was added
    rules_section = updated_sarif["runs"][0]["tool"]["driver"]["rules"]
    assert len(rules_section) == len(expected_rules)
    for rule in expected_rules:
        assert rule in rules_section


def test_process_sarif_string(sample_sarif, expected_rules):
    """Test processing SARIF data from a JSON string."""
    input_data = json.dumps(sample_sarif)
    output_data = process_sarif_string(input_data)

    # Verify the output is valid JSON and contains the expected rules
    updated_sarif = json.loads(output_data)
    rules_section = updated_sarif["runs"][0]["tool"]["driver"]["rules"]
    assert len(rules_section) == len(expected_rules)
    for rule in expected_rules:
        assert rule in rules_section


@patch("pathlib.Path.open", new_callable=mock_open)
@patch("sys.stdout", new_callable=StringIO)
def test_process_sarif_file(mock_stdout, mock_open_file, sample_sarif):
    """Test processing SARIF data from files."""
    input_path = Path("input.sarif")
    output_path = Path("output.sarif")

    # Mock reading input data
    mock_open_file.return_value.read.return_value = json.dumps(sample_sarif)

    # Run the function
    process_sarif_file(input_path, output_path)

    # Verify that the input file was opened for reading
    mock_open_file.assert_any_call("r", encoding="utf-8")

    # Verify that the output file was opened for writing
    mock_open_file.assert_any_call("w", encoding="utf-8")

    # Verify the data written to the output file
    written_data = mock_open_file().write.call_args[0][0]
    updated_sarif = json.loads(written_data)
    assert "runs" in updated_sarif
    assert len(updated_sarif["runs"][0]["tool"]["driver"]["rules"]) > 0


@patch("builtins.open", new_callable=mock_open)
@patch("sys.stdin", new_callable=StringIO)
@patch("sys.stdout", new_callable=StringIO)
def test_process_sarif_file_stdin_stdout(mock_stdout, mock_stdin, mock_file, sample_sarif, expected_rules):
    """Test processing SARIF data with stdin and stdout."""
    mock_stdin.write(json.dumps(sample_sarif))
    mock_stdin.seek(0)

    process_sarif_file(None, None)

    # Verify that output is written to stdout
    output_data = mock_stdout.getvalue()
    updated_sarif = json.loads(output_data)
    rules_section = updated_sarif["runs"][0]["tool"]["driver"]["rules"]
    assert len(rules_section) == len(expected_rules)


def test_empty_sarif():
    """Test handling an empty SARIF file."""
    empty_sarif = {"runs": []}
    output_sarif = add_rules_to_sarif_dict(empty_sarif)
    assert output_sarif == empty_sarif
