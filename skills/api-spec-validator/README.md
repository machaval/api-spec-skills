# API Spec Validator Skill

Agent skill for validating OpenAPI Specification (OAS) files to ensure they are AI-agent-friendly and production-ready.

## Overview

This skill provides both automated and manual validation capabilities for API specifications, checking against 8 comprehensive rules designed to make APIs more usable by AI agents.

## Installation

### Prerequisites

```bash
pip install pyyaml
```

### Usage with Claude

This skill is automatically available when working in this project. Simply ask Claude to:
- "Validate the API spec"
- "Check this OpenAPI specification"
- "Review my OAS file for best practices"

## Validation Rules

1. **OAS Format Required** - Must be valid OpenAPI 3.0/3.1 or Swagger 2.0. RAML specs will be converted to OAS.
2. **Operation IDs Required** - Descriptive IDs (avoid `get_data`, prefer `calculateTaxRate`)
3. **Descriptions with Context** - Include:
   - Legacy field mappings (INTERNAL MAPPING)
   - Contextual warnings (slow endpoints, rate limits)
   - AI aliases for cryptic paths
   - **Recovery instructions for 400 error responses**
4. **Examples Required** - Request and response examples for all endpoints
5. **Type Documentation** - All properties must have descriptions
6. **Output Documentation** - All response schemas fully documented
7. **No Naked Strings** - Use enums for fields with limited options
8. **Required Fields Explicit** - Always list required fields in schema

## Command-Line Usage

### Validate a spec file

```bash
python skills/api-spec-validator/scripts/validate_spec.py path/to/your-api-spec.yaml
```

### Example output

```
======================================================================
API SPEC VALIDATION REPORT
======================================================================

Spec: path/to/your-api-spec.yaml
Total Endpoints: 5
Violations Found: 3
Pass Rate: 85.7%

----------------------------------------------------------------------
VIOLATIONS
----------------------------------------------------------------------

### Rule 2: Operation ID Quality
    (1 violation)
  ❌ GET /users
     operationId 'get_data' is too generic. Use descriptive names like 'calculateTaxRate'

### Rule 7: No Naked Strings
    (2 violations)
  ⚠️  POST /orders (request)
     Property 'status' appears to have limited options but missing enum

======================================================================
✅ VALIDATION PASSED (warnings only)
======================================================================
```

## Examples

### Good Example

See `references/example-good-spec.yaml` for a fully compliant API specification demonstrating all best practices, including:
- Descriptive operation IDs
- Legacy field mappings
- 400 error response recovery instructions
- Comprehensive examples

### Common Violations

See `references/example-violations.yaml` for examples of what NOT to do, with inline comments explaining each violation.

### RAML Conversion

See `references/raml-to-oas-guide.md` for detailed guidance on converting RAML specifications to OAS format.

## Files

```
skills/api-spec-validator/
├── SKILL.md                         # Main skill definition for Claude
├── README.md                        # This file
├── scripts/
│   └── validate_spec.py            # Python validation script
└── references/
    ├── example-good-spec.yaml      # Example of compliant spec
    ├── example-violations.yaml     # Example of violations
    └── raml-to-oas-guide.md        # Guide for converting RAML to OAS
```

## Integration with CI/CD

You can integrate the validator into your CI/CD pipeline:

```yaml
# .github/workflows/validate-specs.yml
name: Validate API Specs
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Validate specs
        run: |
          for spec in specs/*.yaml; do
            python skills/api-spec-validator/scripts/validate_spec.py "$spec"
          done
```

## Contributing

To add new validation rules:

1. Update `SKILL.md` with the new rule description
2. Add validation logic to `validate_spec.py` in the `OASValidator` class
3. Add examples to the reference files
4. Test against both good and bad specs

## License

See project root LICENSE file.
