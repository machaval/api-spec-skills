# API Spec Validator Skill

Agent skill for validating OpenAPI Specification (OAS) files to ensure they are AI-agent-friendly and production-ready.

## Overview

This skill provides both automated and manual validation capabilities for API specifications, checking against 8 comprehensive rules designed to make APIs more usable by AI agents.

## Installation

### Prerequisites

Install the Anypoint CLI tool and API project plugin:

```bash
npm install -g anypoint-cli-v4
anypoint-cli-v4 plugins:install anypoint-cli-api-project-plugin
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

### Basic OAS Format Validation

Validate that the OAS file is syntactically correct:

```bash
anypoint-cli-v4 api-project validate --location=./path/to/folder/with/oas
```

### Full Compliance Validation

Validate against all AI-agent-friendly rules:

```bash
anypoint-cli-v4 api-project validate --location=./path/to/folder/with/oas --local-ruleset skills/api-spec-validator/scripts/ruleset.yaml
```

### Example output

```
Validating API specification...

✓ OAS Format: Valid OpenAPI 3.0.2
✓ Operation IDs: All operations have descriptive IDs

⚠ Violations found:

1. operation-id-camel-case
   - GET /users: operationId 'get_data' must be in camelCase
   - Use descriptive names like 'getUserProfile'

2. no-naked-strings
   - POST /orders (request): Property 'status' must have enum
   - Avoid naked strings with no constraints

Validation completed with 2 violations
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
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install Anypoint CLI
        run: |
          npm install -g anypoint-cli-v4
          anypoint-cli-v4 plugins:install anypoint-cli-api-project-plugin
      - name: Validate specs
        run: |
          for spec_dir in specs/*/; do
            echo "Validating $spec_dir"
            anypoint-cli-v4 api-project validate --location="$spec_dir" --local-ruleset skills/api-spec-validator/scripts/ruleset.yaml
          done
```

## Contributing

To add new validation rules:

1. Update `SKILL.md` with the new rule description
2. Add validation logic to `ruleset.yaml` using AMF Validation Profile format
3. Add examples to the reference files
4. Test against both good and bad specs

### AMF Validation Profile Format

The `ruleset.yaml` uses the AMF Validation Profile format. Example rule:

```yaml
validations:
  my-custom-rule:
    message: Error message for {{property}}
    documentation: |
      Detailed explanation of the rule
    targetClass: apiContract.Operation
    propertyConstraints:
      core.description:
        minCount: 1
```

## License

See project root LICENSE file.
