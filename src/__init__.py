from .bicep_lint_sarif_fixer import (
    add_rules_to_sarif_dict,
    process_sarif_string,
    process_sarif_file,
)

__version__ = "0.0.0a"  # Keep this consistent with the script's version
__author__ = "Balazs Hamorszky"
__all__ = ["add_rules_to_sarif_dict", "process_sarif_string", "process_sarif_file"]
