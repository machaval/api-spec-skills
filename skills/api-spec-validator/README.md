# API Spec Validator Skill

Agent skill for validating OpenAPI Specification (OAS) files to ensure they are AI-agent-friendly and production-ready.

## Overview

This skill provides validation, schema inference, and documentation generation for API specifications:

- **Two-Pass Validation**: First validates OAS syntax, then checks against 8 comprehensive rules designed to make APIs more usable by AI agents
- **Schema Inference Tool**: Automatically generates JSON schemas from examples when schemas are missing
- **Documentation Generator**: Creates markdown documentation with curl examples for each endpoint

## Installation

### Prerequisites

Install the Anypoint CLI tool and API project plugin:

```bash
npm install -g anypoint-cli-v4
anypoint-cli-v4 plugins:install anypoint-cli-api-project-plugin
```

For the schema inference tool:
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

### Two-Pass Validation Workflow

Validation should be performed in **two passes**:

#### Pass 1: Basic OAS Format Validation

First, validate that the OAS file is syntactically correct:

```bash
anypoint-cli-v4 api-project validate --json --location=./path/to/folder/with/oas
```

This checks for valid OAS structure and syntax. **Only proceed to Pass 2 if Pass 1 succeeds.**

#### Pass 2: Full Compliance Validation

After Pass 1 succeeds, validate against all AI-agent-friendly rules:

```bash
anypoint-cli-v4 api-project validate --json --location=./path/to/folder/with/oas --local-ruleset skills/api-spec-validator/scripts/ruleset.yaml
```

This checks all 8 compliance rules for AI-agent friendliness.

### Example output

**Pass 1 (Basic Validation):**
```bash
$ anypoint-cli-v4 api-project validate --location=./api-spec

Validating API specification...
✓ Valid OpenAPI 3.0.2 format
✓ All required fields present
✓ Schema structure valid

Validation passed
```

**Pass 2 (Compliance Validation):**
```bash
$ anypoint-cli-v4 api-project validate --location=./api-spec --local-ruleset skills/api-spec-validator/scripts/ruleset.yaml

Validating API specification...

✓ oas-only: Valid OpenAPI 3.0.2
✓ operation-examples: All operations have examples

⚠ Violations found:

1. operation-id-camel-case
   - GET /users: operationId 'get_data' must be in camelCase
   - Use descriptive names like 'getUserProfile'

2. no-naked-strings
   - POST /orders (request): Property 'status' must have enum
   - Avoid naked strings with no constraints

Validation completed with 2 violations
```

## Schema Inference Tool

When your API spec has examples but missing schemas, use the inference tool to automatically generate them.

### Dry Run (Preview Changes)

```bash
python3 skills/api-spec-validator/scripts/infer_schemas.py path/to/spec.yaml --dry-run
```

### Apply Changes

```bash
python3 skills/api-spec-validator/scripts/infer_schemas.py path/to/spec.yaml
```

### Output

```
Inferring schemas from examples...
File: api-spec.yaml

  ✓ Added schema to POST /users (request) (application/json)
  ✓ Added schema to POST /users (response 200) (application/json)
  ✓ Added schema to GET /users/{id} (response 200) (application/json)

Added 3 schema(s)

Creating backup: api-spec.yaml.backup

✓ Updated api-spec.yaml

⚠️  Note: Generated schemas have placeholder descriptions.
   Please review and update the 'TODO' descriptions with meaningful text.
```

### What Gets Generated

The tool infers:
- **Types**: `string`, `number`, `integer`, `boolean`, `array`, `object`, `null`
- **Formats**: `email`, `uri`, `date` (auto-detected from patterns)
- **Required fields**: All fields marked as required by default
- **Nested structures**: Recursively processes objects and arrays
- **Descriptions**: Placeholder descriptions that need updating

### Post-Inference Workflow

1. Run inference tool to generate schemas
2. Update "TODO" placeholder descriptions
3. Add enums for fields with limited options
4. Adjust required fields if some are optional
5. Run validation to check compliance

## Documentation Generator

Generate markdown documentation with curl examples from your OAS file.

### Usage

```bash
# Generate to default ./docs directory
python3 skills/api-spec-validator/scripts/generate_docs.py path/to/spec.yaml

# Generate to custom directory
python3 skills/api-spec-validator/scripts/generate_docs.py path/to/spec.yaml ./documentation
```

### What Gets Generated

- **README.md**: Overview page with table of contents
- **Individual endpoint pages**: One markdown file per operation with:
  - Parameters table
  - Request body details
  - **Curl command examples** with realistic values
  - Response examples
  - Response codes table

### Example Output Structure

```
docs/
├── README.md                # Overview and table of contents
├── createUser.md           # POST /users documentation
├── getUserById.md          # GET /users/{userId} documentation
└── listOrders.md           # GET /orders documentation
```

### Example Generated Page

See the example curl command from a generated page:

```bash
curl -X POST "https://api.example.com/users" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "age": 28,
  "role": "developer"
}'
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

### Missing Schemas Example

See `references/example-missing-schemas.yaml` for an example spec with examples but no schemas. Use this to test the schema inference tool:

```bash
python3 skills/api-spec-validator/scripts/infer_schemas.py skills/api-spec-validator/references/example-missing-schemas.yaml --dry-run
```

### RAML Conversion

See `references/raml-to-oas-guide.md` for detailed guidance on converting RAML specifications to OAS format.

## Files

```
skills/api-spec-validator/
├── SKILL.md                         # Main skill definition for Claude
├── README.md                        # This file
├── scripts/
│   ├── ruleset.yaml                # AMF validation rules for anypoint-cli-v4
│   ├── infer_schemas.py            # Schema inference tool
│   ├── generate_docs.py            # Documentation generator
│   └── validate_spec.py            # Legacy Python validation script
└── references/
    ├── example-good-spec.yaml      # Example of compliant spec
    ├── example-violations.yaml     # Example of violations
    ├── example-missing-schemas.yaml # Example for schema inference
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

            # Pass 1: Basic validation
            echo "Pass 1: Basic OAS validation..."
            anypoint-cli-v4 api-project validate --location="$spec_dir"

            # Pass 2: Compliance validation
            echo "Pass 2: Compliance validation..."
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
