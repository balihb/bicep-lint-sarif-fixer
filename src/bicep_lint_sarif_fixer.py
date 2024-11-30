import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

__version__ = "0.0.0a"  # Replace with your version

RuleDefinition = dict[str, str | dict[str, str]]
"""
A single rule definition.

Each rule definition contains the following fields:

- `id` (str): The unique identifier of the rule.
- `shortDescription` (dict): A brief description of the rule, typically with a single `text` key.
- `fullDescription` (dict, optional): A detailed description of the rule, typically with a single `text` key.
- `helpUri` (str, optional): A link to documentation for the rule.
- `properties` (dict, optional): Additional metadata for the rule, such as category or severity.
"""

RuleDefs = dict[str, RuleDefinition]
"""
All rule definitions.

A dictionary mapping rule IDs (strings) to their corresponding `RuleDefinition` objects.
"""

rule_defs: RuleDefs = {
    "adminusername-should-not-be-literal": {
        "name": "Admin user name not literal",
        "shortDescription": {"text": "Property 'adminUserName' should not use a literal value. Use a param instead."},
        "helpUri": "https://aka.ms/bicep/linter/adminusername-should-not-be-literal",
        "properties": {"category": "Security"},
    },
    "artifacts-parameters": {
        "name": "Artifacts parameters",
        "shortDescription": {"text": "Follow best practices when including the _artifactsLocation and _artifactsLocationSasToken parameters."},
        "helpUri": "https://aka.ms/bicep/linter/artifacts-parameters",
        "properties": {"category": "BestPractice"},
    },
    "decompiler-cleanup": {
        "name": "Decompiler cleanup",
        "shortDescription": {"text": "Some decompiler imperfections may need to be cleaned up manually."},
        "helpUri": "https://aka.ms/bicep/linter/decompiler-cleanup",
        "properties": {"category": "BestPractice"},
    },
    "explicit-values-for-loc-params": {
        "name": "Explicit values for module location parameters",
        "shortDescription": {"text": "When consuming a module, any location-related parameters that have a default value must be assigned an explicit value."},
        "helpUri": "https://aka.ms/bicep/linter/explicit-values-for-loc-params",
        "properties": {"category": "ResourceLocationRules"},
    },
    "max-asserts": {
        "name": "Max asserts",
        "shortDescription": {"text": "Maximum number of 'assert' statements used."},
        "helpUri": "https://aka.ms/bicep/linter/max-asserts",
        "properties": {"category": "DeploymentError"},
    },
    "max-outputs": {
        "name": "Max outputs",
        "shortDescription": {"text": "Maximum number of outputs used."},
        "helpUri": "https://aka.ms/bicep/linter/max-outputs",
        "properties": {"category": "DeploymentError"},
    },
    "max-params": {
        "name": "Max parameters",
        "shortDescription": {"text": "Maximum number of parameters used."},
        "helpUri": "https://aka.ms/bicep/linter/max-params",
        "properties": {"category": "DeploymentError"},
    },
    "max-resources": {
        "name": "Max resources",
        "shortDescription": {"text": "Maximum number of resources used."},
        "helpUri": "https://aka.ms/bicep/linter/max-resources",
        "properties": {"category": "DeploymentError"},
    },
    "max-variables": {
        "name": "Max variables",
        "shortDescription": {"text": "Maximum number of variables used."},
        "helpUri": "https://aka.ms/bicep/linter/max-variables",
        "properties": {"category": "DeploymentError"},
    },
    "no-conflicting-metadata": {
        "name": "No conflicting metadata",
        "shortDescription": {"text": "Metadata properties whose value is set by a separate decorator should not be set via the '@metadata()' decorator."},
        "helpUri": "https://aka.ms/bicep/linter/no-conflicting-metadata",
        "properties": {"category": "PotentialCodeIssues"},
    },
    "no-deployments-resources": {
        "name": "No deployments resources",
        "shortDescription": {"text": "Bicep modules are recommended instead of representing nested or linked deployments as a resource."},
        "helpUri": "https://aka.ms/bicep/linter/no-deployments-resources",
        "properties": {"category": "BestPractice"},
    },
    "no-hardcoded-env-urls": {
        "name": "No hardcoded environment URLs",
        "shortDescription": {"text": "Environment URLs should not be hardcoded. Use the environment() function to ensure compatibility across clouds."},
        "helpUri": "https://aka.ms/bicep/linter/no-hardcoded-env-urls",
        "properties": {"category": "BestPractice"},
    },
    "no-hardcoded-location": {
        "name": "No hardcoded locations",
        "shortDescription": {
            "text": "A resource's location should not use a hard-coded string or variable value. It should use a parameter, an expression, or the string 'global'."
        },
        "helpUri": "https://aka.ms/bicep/linter/no-hardcoded-location",
        "properties": {"category": "ResourceLocationRules"},
    },
    "no-loc-expr-outside-params": {
        "name": "No location expressions outside of parameter default values",
        "shortDescription": {"text": "Functions resourceGroup().location and deployment().location should only be used as the default value of a parameter."},
        "helpUri": "https://aka.ms/bicep/linter/no-loc-expr-outside-params",
        "properties": {"category": "ResourceLocationRules"},
    },
    "nested-deployment-template-scoping": {
        "name": "Nested deployment template scoping",
        "shortDescription": {"text": "Nested deployment resources cannot refer to top-level symbols from within the 'template' property when inner-scoped evaluation is used."},
        "helpUri": "https://aka.ms/bicep/linter/nested-deployment-template-scoping",
        "properties": {"category": "DeploymentError"},
    },
    "no-unnecessary-dependson": {
        "name": "No unnecessary dependsOn entries",
        "shortDescription": {"text": "No unnecessary dependsOn."},
        "helpUri": "https://aka.ms/bicep/linter/no-unnecessary-dependson",
        "properties": {"category": "BestPractice"},
    },
    "no-unused-existing-resources": {
        "name": "No unused existing resources",
        "shortDescription": {"text": "All existing resources must be used."},
        "helpUri": "https://aka.ms/bicep/linter/no-unused-existing-resources",
        "properties": {"category": "BestPractice"},
    },
    "no-unused-params": {
        "name": "No unused parameters",
        "shortDescription": {"text": "All parameters must be used."},
        "helpUri": "https://aka.ms/bicep/linter/no-unused-params",
        "properties": {"category": "BestPractice"},
    },
    "no-unused-vars": {
        "name": "No unused variables",
        "shortDescription": {"text": "All variables must be used."},
        "helpUri": "https://aka.ms/bicep/linter/no-unused-vars",
        "properties": {"category": "BestPractice"},
    },
    "outputs-should-not-contain-secrets": {
        "name": "Outputs should not contain secrets",
        "shortDescription": {"text": "Outputs should not contain secrets."},
        "helpUri": "https://aka.ms/bicep/linter/outputs-should-not-contain-secrets",
        "properties": {"category": "Security"},
    },
    "prefer-interpolation": {
        "name": "Prefer interpolation",
        "shortDescription": {"text": "Use string interpolation instead of the concat function."},
        "helpUri": "https://aka.ms/bicep/linter/prefer-interpolation",
        "properties": {"category": "Style"},
    },
    "prefer-unquoted-property-names": {
        "name": "Prefer unquoted property names",
        "shortDescription": {"text": "Property names that are valid identifiers should be declared without quotation marks and accessed using dot notation."},
        "helpUri": "https://aka.ms/bicep/linter/prefer-unquoted-property-names",
        "properties": {"category": "Style"},
    },
    "secure-secrets-in-params": {
        "name": "Secure secrets in parameters",
        "shortDescription": {"text": "Parameters that represent secrets must be secure."},
        "helpUri": "https://aka.ms/bicep/linter/secure-secrets-in-params",
        "properties": {"category": "Security"},
    },
    "secure-parameter-default": {
        "name": "Secure parameter default",
        "shortDescription": {"text": "Secure parameters should not have hardcoded defaults (except for empty or newGuid())."},
        "helpUri": "https://aka.ms/bicep/linter/secure-parameter-default",
        "properties": {"category": "Security"},
    },
    "secure-params-in-nested-deploy": {
        "name": "Secure parameters in nested deployments",
        "shortDescription": {"text": "Outer-scoped nested deployment resources should not be used for secure parameters or list* functions."},
        "helpUri": "https://aka.ms/bicep/linter/secure-params-in-nested-deploy",
        "properties": {"category": "Security"},
    },
    "simplify-interpolation": {
        "name": "Simplify interpolation",
        "shortDescription": {"text": "Remove unnecessary string interpolation."},
        "helpUri": "https://aka.ms/bicep/linter/simplify-interpolation",
        "properties": {"category": "Style"},
    },
    "simplify-json-nul": {
        "name": "Simplify JSON null",
        "shortDescription": {"text": "Simplify json('null') to null"},
        "helpUri": "https://aka.ms/bicep/linter/simplify-json-nul",
        "properties": {"category": "BestPractice"},
    },
    "use-parent-property": {
        "name": "Use parent property",
        "shortDescription": {"text": "Use the parent property instead of formatting child resource names with '/' characters."},
        "helpUri": "https://aka.ms/bicep/linter/use-parent-property",
        "properties": {"category": "BestPractice"},
    },
    "protect-commandtoexecute-secrets": {
        "name": "Protect commandToExecute secrets",
        "shortDescription": {"text": "Use protectedSettings for commandToExecute secrets."},
        "helpUri": "https://aka.ms/bicep/linter/protect-commandtoexecute-secrets",
        "properties": {"category": "Security"},
    },
    "use-recent-api-versions": {
        "name": "Use recent API versions",
        "shortDescription": {"text": "Use recent API versions."},
        "helpUri": "https://aka.ms/bicep/linter/use-recent-api-versions",
        "properties": {"category": "BestPractice"},
    },
    "use-recent-module-versions": {
        "name": "Use recent module versions",
        "shortDescription": {"text": "Use recent module versions."},
        "helpUri": "https://aka.ms/bicep/linter/use-recent-module-versions",
        "properties": {"category": "BestPractice"},
    },
    "use-resource-id-functions": {
        "name": "Use resource ID functions",
        "shortDescription": {"text": "Properties representing a resource ID must be generated appropriately."},
        "helpUri": "https://aka.ms/bicep/linter/use-resource-id-functions",
        "properties": {"category": "BestPractice"},
    },
    "use-resource-symbol-reference": {
        "name": "Use resource symbol reference",
        "shortDescription": {"text": "Use a direct resource symbol reference instead of 'reference' or 'list*' functions."},
        "helpUri": "https://aka.ms/bicep/linter/use-resource-symbol-reference",
        "properties": {"category": "BestPractice"},
    },
    "use-safe-access": {
        "name": "Use safe access",
        "shortDescription": {"text": "Use the safe access (.?) operator instead of checking object contents with the 'contains' function."},
        "helpUri": "https://aka.ms/bicep/linter/use-safe-access",
        "properties": {"category": "BestPractice"},
    },
    "use-secure-value-for-secure-inputs": {
        "name": "Use secure value for secure inputs",
        "shortDescription": {"text": "Resource properties expecting secure input should be assigned secure values."},
        "helpUri": "https://aka.ms/bicep/linter/use-secure-value-for-secure-inputs",
        "properties": {"category": "Security"},
    },
    "use-stable-resource-identifiers": {
        "name": "Use stable resource identifier",
        "shortDescription": {"text": "Resource identifiers should be reproducible outside of their initial deployment context. "},
        "helpUri": "https://aka.ms/bicep/linter/use-stable-resource-identifiers",
        "properties": {"category": "PotentialCodeIssues"},
    },
    "use-stable-vm-image": {
        "name": "Use stable VM image",
        "shortDescription": {"text": "Virtual machines shouldn't use preview images."},
        "helpUri": "https://aka.ms/bicep/linter/use-stable-vm-image",
        "properties": {"category": "BestPractice"},
    },
    "what-if-short-circuiting": {
        "name": "What-if short-circuiting",
        "shortDescription": {"text": "Runtime values should not be used to determine resource IDs."},
        "helpUri": "https://aka.ms/bicep/linter/what-if-short-circuiting",
        "properties": {"category": "PotentialCodeIssues"},
    },
}
"""
Definitions for Bicep Linter rules.

Each key is a rule ID, and the value is a `RuleDefinition` object.

Information sources:

- `Bicep Linter Docs <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter>`__
- `Bicep Linter Rules in the Bicep Source <https://github.com/Azure/bicep/tree/main/src/Bicep.Core/Analyzers/Linter/Rules>`__
- `Bicep Linter Rule Descriptions <https://github.com/Azure/bicep/blob/main/src/Bicep.Core/CoreResources.resx>`__

Example:

.. code-block:: python

    rule_defs = {
        "adminusername-should-not-be-literal": {
            "name": "Admin user name not literal",
            "shortDescription": {"text": "Property 'adminUserName' should not use a literal value. Use a param instead."},
            "helpUri": "https://aka.ms/bicep/linter/adminusername-should-not-be-literal",
            "properties": {"category": "Security"}
        }
    }
"""

category_to_diagnostic_level: dict[str, str] = {
    "BestPractice": "warning",
    "DeploymentError": "error",
    "Portability": "note",
    "PotentialCodeIssues": "warning",
    "ResourceLocationRules": "note",
    "Security": "warning",
    "Style": "warning",
}
"""Bicep lint issue category to diagnostic level

`LinterRuleBase <https://github.com/Azure/bicep/blob/main/src/Bicep.Core/Analyzers/Linter/LinterRuleBase.cs>`__
"""


def _parse_args() -> argparse.ArgumentParser:
    """Parse command-line arguments.

    Returns:
        argparse.ArgumentParser: Parsed arguments with input and output paths.
    """
    parser = argparse.ArgumentParser(description="Fix issues in SARIF files generated by Bicep Lint.")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=None,
        help="Path to the input SARIF file (default: stdin). Use '-' for stdin.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to the output SARIF file (default: stdout). Use '-' for stdout.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version of the script and exit.",
    )
    return parser


def add_rules_to_sarif_dict(sarif_data: dict, rule_definitions: RuleDefs = None) -> dict:
    """
    Add rule definitions to SARIF data.

    Modifies the SARIF data by adding a "rules" section to the tool extensions
    based on the provided rule definitions.

    Args:
        sarif_data (dict): A dictionary containing SARIF content.
        rule_definitions (RuleDefs | None): A dictionary mapping rule IDs to their definitions.
            If `None`, `rule_defs` is used as the default.

    Returns:
        dict: The updated SARIF data with added rules.
    """
    if rule_definitions is None:
        rule_definitions = rule_defs
    for run in sarif_data.get("runs", []):
        tool = run.setdefault("tool", {})
        driver = tool.setdefault("driver", {})
        rules_section = driver.setdefault("rules", [])

        for result in run.get("results", []):
            rule_id = result.get("ruleId")
            if rule_id in rule_definitions:
                rule_definition = rule_definitions[rule_id]
                rule = {
                    "id": rule_id,
                    "name": rule_definition["name"],
                    "shortDescription": rule_definition["shortDescription"],
                    "helpUri": rule_definition["helpUri"],
                    "properties": rule_definition["properties"],
                    "defaultConfiguration": {"level": category_to_diagnostic_level[rule_definition["properties"]["category"]]},
                }
                if rule not in rules_section:
                    rules_section.append(rule)
    return sarif_data


def process_sarif_string(input_data: str, rule_definitions: RuleDefs = None) -> str:
    """
    Process SARIF data provided as a string.

    Args:
        input_data (str): The SARIF data as a JSON string.
        rule_definitions (RuleDefs | None): A dictionary mapping rule IDs to their definitions.

    Returns:
        str: The processed SARIF data as a JSON string.
    """
    if rule_definitions is None:
        rule_definitions = rule_defs
    sarif_data = json.loads(input_data)
    processed_data = add_rules_to_sarif_dict(sarif_data, rule_definitions)
    return json.dumps(processed_data, indent=4)


def process_sarif_file(
    input_path: Path | str | None = None,
    output_path: Path | str | None = None,
    rule_definitions: RuleDefs | None = None,
):
    """
    Process SARIF data from input and output file paths.

    Reads SARIF data from the input file, applies rule processing, and writes
    the processed data to the output file. If no input file is provided, reads
    from stdin. If no output file is provided, writes to stdout.

    Args:
        input_path (Path | str | None): Path to the input SARIF file, `-` for stdin, or `None` for default.
        output_path (Path | str | None): Path to the output SARIF file, `-` for stdout, or `None` for default.
        rule_definitions (RuleDefs | None): A dictionary mapping rule IDs to their definitions.

    Raises:
        FileNotFoundError: If the input file does not exist.
    """
    if rule_definitions is None:
        rule_definitions = rule_defs

    # Read input
    if input_path == "-" or input_path is None:
        input_data = sys.stdin.read()
    else:
        with Path(input_path).open("r", encoding="utf-8") as infile:
            input_data = infile.read()

    # Process data
    processed_data = process_sarif_string(input_data, rule_definitions)

    # Handle case where input and output are the same
    if input_path == output_path and input_path not in [None, "-"]:
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmpfile:
            tmpfile.write(processed_data)
            temp_path = Path(tmpfile.name)
        shutil.move(temp_path, Path(input_path))  # Overwrite the input file
    elif output_path == "-" or output_path is None:
        sys.stdout.write(processed_data)
    else:
        with Path(output_path).open("w", encoding="utf-8") as outfile:
            outfile.write(processed_data)


def main():
    args = _parse_args().parse_args()
    process_sarif_file(args.input, args.output, rule_defs)


# pragma: no cover
if __name__ == "__main__":
    main()
