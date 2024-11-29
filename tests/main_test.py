import json
from io import StringIO
from unittest.mock import patch, mock_open

import pytest

from bicep_lint_sarif_fixer import main, __version__


@pytest.fixture
def sample_sarif():
    """Fixture for sample SARIF data."""
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


@patch("sys.argv", ["bicep_lint_sarif_fixer", "-i", "input.sarif", "-o", "output.sarif"])
@patch("pathlib.Path.open", new_callable=mock_open, read_data='{"runs": []}')
@patch("sys.stdout", new_callable=StringIO)
def test_main_with_files(mock_stdout, mock_open_path, sample_sarif):
    """
    Test the main function with input and output files specified.
    """
    # Mock input file content
    mock_open_path.return_value.read.return_value = json.dumps(sample_sarif)

    # Run main
    main()

    # Verify input file was read
    mock_open_path.assert_any_call("r", encoding="utf-8")

    # Verify output file was written
    mock_open_path.assert_any_call("w", encoding="utf-8")

    # Verify written content
    written_data = mock_open_path().write.call_args[0][0]
    written_json = json.loads(written_data)
    assert "runs" in written_json
    assert len(written_json["runs"][0]["results"]) == 3  # Ensure results are preserved



@patch("sys.argv", ["bicep_lint_sarif_fixer", "-i", "-", "-o", "-"])
@patch("sys.stdin", new_callable=StringIO)
@patch("sys.stdout", new_callable=StringIO)
def test_main_with_stdin_stdout(mock_stdout, mock_stdin, sample_sarif):
    """
    Test the main function with stdin and stdout.
    """
    # Mock stdin data
    mock_stdin.write(json.dumps(sample_sarif))
    mock_stdin.seek(0)

    # Run main
    main()

    # Verify stdout content
    output_data = json.loads(mock_stdout.getvalue())
    assert "runs" in output_data
    assert len(output_data["runs"][0]["results"]) == 3


@patch("sys.argv", ["bicep_lint_sarif_fixer", "--version"])
@patch("sys.stdout", new_callable=StringIO)
def test_main_version(mock_stdout):
    """
    Test the --version argument for the main function.
    """
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0
    assert f"{__version__}" in mock_stdout.getvalue()
