#!/usr/bin/env python3
"""
API Spec Validator

Validates OpenAPI Specification files against AI-agent-friendly rules.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


@dataclass
class Violation:
    """Represents a validation rule violation"""
    rule: str
    path: str
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationReport:
    """Complete validation report"""
    spec_path: str
    total_endpoints: int = 0
    violations: List[Violation] = field(default_factory=list)
    passed_rules: List[str] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage"""
        total_checks = len(self.violations) + len(self.passed_rules)
        if total_checks == 0:
            return 100.0
        return (len(self.passed_rules) / total_checks) * 100

    def has_errors(self) -> bool:
        """Check if report has any errors"""
        return any(v.severity == "error" for v in self.violations)


class OASValidator:
    """OpenAPI Specification Validator"""

    # Generic operation ID patterns to flag
    GENERIC_OPERATION_IDS = {
        'get_data', 'post_data', 'put_data', 'delete_data',
        'update', 'create', 'delete', 'fetch', 'get', 'post', 'put',
        'retrieve', 'add', 'remove', 'read', 'write'
    }

    # Patterns indicating legacy/cryptic field names
    LEGACY_PATTERNS = [
        r'^v\d+_',  # v1_status_code, v2_field
        r'legacy_',  # legacy_tier
        r'old_',     # old_category
        r'^[a-z]_code$',  # a_code, b_code
    ]

    def __init__(self, spec_path: str):
        self.spec_path = Path(spec_path)
        self.spec: Dict[str, Any] = {}
        self.report = ValidationReport(spec_path=str(spec_path))

    def load_spec(self) -> bool:
        """Load and parse the OAS file"""
        try:
            with open(self.spec_path, 'r') as f:
                content = f.read()

                # Try YAML first, then JSON
                try:
                    self.spec = yaml.safe_load(content)
                except yaml.YAMLError:
                    try:
                        self.spec = json.loads(content)
                    except json.JSONDecodeError:
                        print(f"Error: Failed to parse {self.spec_path} as YAML or JSON")
                        return False
            return True
        except FileNotFoundError:
            print(f"Error: File not found: {self.spec_path}")
            return False
        except Exception as e:
            print(f"Error loading spec: {e}")
            return False

    def validate(self) -> ValidationReport:
        """Run all validation rules"""
        if not self.load_spec():
            sys.exit(1)

        # Rule 1: OAS format check
        self._validate_oas_format()

        # Get all paths
        paths = self.spec.get('paths', {})

        # Count total endpoints
        for path, methods in paths.items():
            for method in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                if method in methods:
                    self.report.total_endpoints += 1

        # Validate each endpoint
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                    endpoint_path = f"{method.upper()} {path}"
                    self._validate_operation(endpoint_path, path, method, operation)

        return self.report

    def _validate_oas_format(self):
        """Rule 1: Validate OAS format"""
        openapi_version = self.spec.get('openapi', self.spec.get('swagger'))

        if not openapi_version:
            self.report.violations.append(Violation(
                rule="Rule 1: OAS Format",
                path="root",
                message="Missing 'openapi' or 'swagger' version field"
            ))
        elif isinstance(openapi_version, str):
            if openapi_version.startswith('3.0') or openapi_version.startswith('3.1') or openapi_version.startswith('2.0'):
                self.report.passed_rules.append("Rule 1: Valid OAS format")
            else:
                self.report.violations.append(Violation(
                    rule="Rule 1: OAS Format",
                    path="root",
                    message=f"Unsupported OAS version: {openapi_version}"
                ))
        else:
            self.report.violations.append(Violation(
                rule="Rule 1: OAS Format",
                path="root",
                message="Invalid 'openapi' version format"
            ))

    def _validate_operation(self, endpoint_path: str, path: str, method: str, operation: Dict):
        """Validate a single operation against all rules"""
        # Rule 2: Operation ID
        self._validate_operation_id(endpoint_path, operation)

        # Rule 3: Description
        self._validate_description(endpoint_path, path, operation)

        # Rule 3 (Extended): Legacy error responses
        self._validate_error_responses(endpoint_path, operation)

        # Rule 4: Examples
        self._validate_examples(endpoint_path, operation)

        # Rule 5 & 6: Type documentation
        self._validate_type_documentation(endpoint_path, operation)

        # Rule 7: No naked strings
        self._validate_no_naked_strings(endpoint_path, operation)

        # Rule 8: Required fields
        self._validate_required_fields(endpoint_path, operation)

    def _validate_operation_id(self, endpoint_path: str, operation: Dict):
        """Rule 2: Validate operation ID"""
        operation_id = operation.get('operationId')

        if not operation_id:
            self.report.violations.append(Violation(
                rule="Rule 2: Operation ID Required",
                path=endpoint_path,
                message="Missing operationId"
            ))
            return

        # Check for generic names
        if operation_id.lower() in self.GENERIC_OPERATION_IDS:
            self.report.violations.append(Violation(
                rule="Rule 2: Operation ID Quality",
                path=endpoint_path,
                message=f"operationId '{operation_id}' is too generic. Use descriptive names like 'calculateTaxRate' or 'provisionCloudServer'"
            ))
            return

        # Check for underscore_case generic patterns
        parts = operation_id.split('_')
        if len(parts) == 2 and parts[0] in ['get', 'post', 'put', 'delete', 'update', 'create', 'fetch']:
            self.report.violations.append(Violation(
                rule="Rule 2: Operation ID Quality",
                path=endpoint_path,
                message=f"operationId '{operation_id}' is too generic. Be more specific about what is being {parts[0]}"
            ))

    def _validate_description(self, endpoint_path: str, path: str, operation: Dict):
        """Rule 3: Validate description and check for needed warnings"""
        description = operation.get('description', '')
        summary = operation.get('summary', '')

        if not description:
            self.report.violations.append(Violation(
                rule="Rule 3: Description Required",
                path=endpoint_path,
                message="Missing description field"
            ))

        # Check for cryptic paths needing AI alias
        if re.search(r'/(rpc|action|proc)/.*\d+', path) and not summary:
            self.report.violations.append(Violation(
                rule="Rule 3: AI Alias Needed",
                path=endpoint_path,
                message=f"Cryptic path '{path}' should have a 'summary' field as AI alias (e.g., 'Create Support Ticket')",
                severity="warning"
            ))

    def _validate_error_responses(self, endpoint_path: str, operation: Dict):
        """Rule 3 (Extended): Validate legacy error response handling"""
        responses = operation.get('responses', {})

        # Check for 400 responses
        if '400' in responses:
            response_400 = responses['400']
            description = response_400.get('description', '')

            # Check if response has error codes in schema
            has_error_codes = False
            content = response_400.get('content', {})
            for media_type, schema_info in content.items():
                schema = schema_info.get('schema', {})
                properties = schema.get('properties', {})

                # Look for error code fields
                if 'errorCode' in properties or 'error_code' in properties or 'code' in properties:
                    has_error_codes = True
                    break

            # If error codes exist, check for recovery instructions
            if has_error_codes and 'RECOVERY INSTRUCTIONS' not in description:
                self.report.violations.append(Violation(
                    rule="Rule 3: Legacy Error Response Handling",
                    path=f"{endpoint_path} (400 response)",
                    message="400 response with error codes should include 'RECOVERY INSTRUCTIONS' in description to help AI agents handle errors",
                    severity="warning"
                ))

    def _validate_examples(self, endpoint_path: str, operation: Dict):
        """Rule 4: Validate examples"""
        has_example = False

        # Check request body examples
        request_body = operation.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            for media_type, schema_info in content.items():
                if 'examples' in schema_info or 'example' in schema_info:
                    has_example = True

        # Check response examples
        responses = operation.get('responses', {})
        for status_code, response in responses.items():
            if status_code.startswith('2'):  # Success responses
                content = response.get('content', {})
                for media_type, schema_info in content.items():
                    if 'examples' in schema_info or 'example' in schema_info:
                        has_example = True

        if not has_example and (request_body or responses):
            self.report.violations.append(Violation(
                rule="Rule 4: Examples Required",
                path=endpoint_path,
                message="Missing examples in request or response"
            ))

    def _validate_type_documentation(self, endpoint_path: str, operation: Dict):
        """Rule 5 & 6: Validate type documentation"""
        # Check request body schemas
        request_body = operation.get('requestBody', {})
        if request_body:
            self._check_schema_documentation(
                endpoint_path,
                request_body.get('content', {}),
                "request"
            )

        # Check response schemas
        responses = operation.get('responses', {})
        for status_code, response in responses.items():
            self._check_schema_documentation(
                endpoint_path,
                response.get('content', {}),
                f"response {status_code}"
            )

    def _check_schema_documentation(self, endpoint_path: str, content: Dict, location: str):
        """Check if schema properties are documented"""
        for media_type, schema_info in content.items():
            schema = schema_info.get('schema', {})
            if '$ref' in schema:
                # Reference to component - would need to resolve
                continue

            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                if 'description' not in prop_schema:
                    self.report.violations.append(Violation(
                        rule="Rule 5: Type Documentation Required",
                        path=f"{endpoint_path} ({location})",
                        message=f"Property '{prop_name}' missing description"
                    ))

                # Check for legacy field patterns
                for pattern in self.LEGACY_PATTERNS:
                    if re.match(pattern, prop_name):
                        desc = prop_schema.get('description', '')
                        if 'INTERNAL MAPPING' not in desc:
                            self.report.violations.append(Violation(
                                rule="Rule 3: Legacy Field Mapping",
                                path=f"{endpoint_path} ({location})",
                                message=f"Legacy field '{prop_name}' should have 'INTERNAL MAPPING' in description to explain encoding",
                                severity="warning"
                            ))

    def _validate_no_naked_strings(self, endpoint_path: str, operation: Dict):
        """Rule 7: No naked strings with limited options"""
        # This is a heuristic check - looks for strings with "or" in description

        def check_properties(properties: Dict, location: str):
            for prop_name, prop_schema in properties.items():
                if prop_schema.get('type') == 'string':
                    description = prop_schema.get('description', '').lower()
                    # Check if description suggests limited options
                    if any(indicator in description for indicator in [' or ', 'either', 'one of', 'can be']):
                        if 'enum' not in prop_schema:
                            self.report.violations.append(Violation(
                                rule="Rule 7: No Naked Strings",
                                path=f"{endpoint_path} ({location})",
                                message=f"Property '{prop_name}' appears to have limited options but missing enum",
                                severity="warning"
                            ))

        # Check request body
        request_body = operation.get('requestBody', {})
        for media_type, schema_info in request_body.get('content', {}).items():
            schema = schema_info.get('schema', {})
            properties = schema.get('properties', {})
            check_properties(properties, "request")

        # Check responses
        responses = operation.get('responses', {})
        for status_code, response in responses.items():
            for media_type, schema_info in response.get('content', {}).items():
                schema = schema_info.get('schema', {})
                properties = schema.get('properties', {})
                check_properties(properties, f"response {status_code}")

    def _validate_required_fields(self, endpoint_path: str, operation: Dict):
        """Rule 8: Required fields must be explicit"""
        def check_schema(schema: Dict, location: str):
            properties = schema.get('properties', {})
            required = schema.get('required', [])

            if properties and not required:
                self.report.violations.append(Violation(
                    rule="Rule 8: Required Fields Explicit",
                    path=f"{endpoint_path} ({location})",
                    message="Schema has properties but missing 'required' array. Explicitly list required fields or set to empty array []",
                    severity="warning"
                ))

        # Check request body
        request_body = operation.get('requestBody', {})
        for media_type, schema_info in request_body.get('content', {}).items():
            schema = schema_info.get('schema', {})
            if schema and '$ref' not in schema:
                check_schema(schema, "request")

        # Check responses
        responses = operation.get('responses', {})
        for status_code, response in responses.items():
            for media_type, schema_info in response.get('content', {}).items():
                schema = schema_info.get('schema', {})
                if schema and '$ref' not in schema:
                    check_schema(schema, f"response {status_code}")


def print_report(report: ValidationReport):
    """Print validation report"""
    print("\n" + "="*70)
    print("API SPEC VALIDATION REPORT")
    print("="*70)
    print(f"\nSpec: {report.spec_path}")
    print(f"Total Endpoints: {report.total_endpoints}")
    print(f"Violations Found: {len(report.violations)}")
    print(f"Pass Rate: {report.pass_rate:.1f}%")

    if report.violations:
        print("\n" + "-"*70)
        print("VIOLATIONS")
        print("-"*70)

        # Group by rule
        by_rule: Dict[str, List[Violation]] = {}
        for violation in report.violations:
            by_rule.setdefault(violation.rule, []).append(violation)

        for rule, violations in sorted(by_rule.items()):
            print(f"\n### {rule}")
            print(f"    ({len(violations)} violation{'s' if len(violations) != 1 else ''})")
            for v in violations:
                icon = "⚠️ " if v.severity == "warning" else "❌"
                print(f"  {icon} {v.path}")
                print(f"     {v.message}")

    if report.passed_rules:
        print("\n" + "-"*70)
        print("PASSED")
        print("-"*70)
        for rule in report.passed_rules:
            print(f"  ✓ {rule}")

    print("\n" + "="*70)

    if report.has_errors():
        print("❌ VALIDATION FAILED")
    else:
        print("✅ VALIDATION PASSED (warnings only)")
    print("="*70 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_spec.py <path-to-spec.yaml>")
        sys.exit(1)

    spec_path = sys.argv[1]

    validator = OASValidator(spec_path)
    report = validator.validate()

    print_report(report)

    # Exit with error code if validation failed
    sys.exit(1 if report.has_errors() else 0)


if __name__ == "__main__":
    main()
