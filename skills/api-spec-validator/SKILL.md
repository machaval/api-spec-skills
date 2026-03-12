---
name: api-spec-validator
description: This skill should be used when the user asks to "validate API spec", "check OpenAPI spec", "lint OAS", "review API specification", "convert RAML to OAS", or mentions validating, checking, or reviewing OpenAPI/OAS/Swagger/RAML specifications against best practices.
metadata: 
  version: 1.0.0
  author: "Mariano de Achaval"
---

# API Spec Validator

This skill validates OpenAPI Specification (OAS) files against a comprehensive set of rules designed to ensure API specifications are AI-agent-friendly and production-ready.

## API Project structure.

Every api specification should be organized as an Anypoint API Project with the following structure:

```api-project/
├── api.yaml
├── README.md
├── docs/
├── exchange.json
```

Exchange.json needs to have the following shape:
```json
{
    "main": "api.yaml",
    "name": "<name-of-the-api>",
    "organizationId": "8bfc8bbf-5508-419e-aadc-77dfe18a8172",
    "groupId": "f1e97bc6-315a-4490-82a7-23abe036327a.anypoint-platform",
    "assetId": "<same-as-the-folder>",
    "version": "<any-semver-version default 1.0.0>",    
    "apiVersion": "v1",
    "classifier": "oas",
    "dependencies": [],    
    "originalFormatVersion": "3.0"
}
```

## When to Use This Skill

Use this skill when:
- Validating or reviewing OpenAPI/OAS/Swagger specifications
- Checking API specs for completeness and best practices
- Ensuring API specs are optimized for AI agent consumption
- Auditing API documentation quality

## Validation Rules

### Rule 1: OAS Format Required
All API specifications must be written in OpenAPI Specification (OAS) format. Supported versions:
- OAS 3.0.x
- OAS 3.1.x
- Swagger 2.0 (legacy support)

**Translation**: All APIs should be written in OAS 3 or bigger and in yaml. 

### Rule 2: Operation IDs Required
Every endpoint operation must have an `operationId` that is:
- **Descriptive and specific**: Clearly indicates what the operation does
- **Avoids generic names**: ❌ `get_data`, `update`, `post_item`, `fetch`
- **Follows verb-noun pattern**: ✅ `calculateTaxRate`, `provisionCloudServer`, `getUserPreferences`, `cancelSubscription`

**Good examples:**
- `calculateTaxRate` - specific action + specific domain
- `provisionCloudServer` - clear verb + clear resource
- `getUserPaymentHistory` - specific action + specific data

**Bad examples:**
- `get_data` - too generic
- `update` - missing context
- `create` - which resource?
- `fetch` - fetch what?

### Rule 3: Descriptions Required with Context
Every endpoint operation must have a `description` field. Apply special handling for:

#### Legacy Field Mapping
If a field name is cryptic or legacy (e.g., `v1_status_code`, `legacy_tier`, `old_category`), override its description with clear mapping:

```yaml
description: "INTERNAL MAPPING: This represents the customer's loyalty tier. Map 'A' to Gold, 'B' to Silver, 'C' to Bronze."
```

#### Contextual Warnings
Add "WARNING" notes in descriptions for important operational considerations:

```yaml
description: "WARNING: This endpoint is slow. Expect a 5-second delay. Do not retry before 10 seconds."
```

```yaml
description: "WARNING: This endpoint is rate-limited to 10 requests per minute per user."
```

#### AI Aliases for Cryptic Paths
If the path is cryptic (e.g., `POST /rpc/v2/action_4`, `GET /api/v1/proc/17`), use the `summary` field to give it a human-readable "AI Alias":

```yaml
summary: "Create Support Ticket"
description: "Creates a new support ticket in the system."
```

#### Legacy Error Response Handling
For legacy 400 Bad Request responses, add recovery instructions in the response description to help AI agents parse error bodies and retry correctly:

```yaml
responses:
  '400':
    description: "Bad Request. RECOVERY INSTRUCTIONS: If the response contains 'ERR_04', the date format was wrong. Re-try using YYYY-MM-DD format. If 'ERR_12', the amount exceeded maximum limit - reduce amount to under $10,000."
    content:
      application/json:
        schema:
          type: object
          properties:
            errorCode:
              type: string
              enum: [ERR_04, ERR_12, ERR_15]
              description: "Error code indicating the type of validation failure"
            message:
              type: string
              description: "Human-readable error message"
        examples:
          dateFormatError:
            summary: Date format error
            value:
              errorCode: "ERR_04"
              message: "Invalid date format"
```

**Pattern for recovery instructions:**
- Start with "RECOVERY INSTRUCTIONS:" in the 400 response description
- Map each error code to specific corrective action
- Be explicit about what to change (format, value range, required fields, etc.)
- Prevent unnecessary retries by being specific about the fix needed

### Rule 4: Examples Required
Every endpoint operation must have at least one example demonstrating:
- Request parameters (if applicable)
- Request body (if applicable)
- Successful response (200/201)

Use the `examples` field in request bodies and responses:

```yaml
requestBody:
  content:
    application/json:
      examples:
        createUser:
          summary: Create new user
          value:
            name: "John Doe"
            email: "john@example.com"
```

### Rule 5: Type Documentation Required
All schema properties must include a `description` field explaining:
- What the field represents
- Valid values or ranges
- Business logic or constraints

```yaml
properties:
  status:
    type: string
    description: "Current order status. Transitions from 'pending' → 'processing' → 'shipped' → 'delivered'."
```

### Rule 6: Output Types Documentation Required
All response schemas must be fully documented with:
- Description for each property
- Data types clearly specified
- Nullable fields explicitly marked

### Rule 7: No Naked Strings
If a field has a limited set of options, it must have an `enum` defined. Never use plain `string` type for constrained values.

**Bad:**
```yaml
status:
  type: string
  description: "Order status (pending, shipped, or delivered)"
```

**Good:**
```yaml
status:
  type: string
  enum: [pending, shipped, delivered]
  description: "Current order status"
```

### Rule 8: Required Fields Explicit
Always explicitly list required fields in the schema's `required` array to prevent AI agents from "guessing" optional parameters.

```yaml
properties:
  name:
    type: string
  email:
    type: string
  age:
    type: integer
required:
  - name
  - email
```

## Tools Available

This skill provides three main tools:

1. **Two-Pass Validation Tool**:
   - Pass 1: Validates OAS syntax and structure
   - Pass 2: Validates against AI-agent-friendly rules
2. **Schema Inference Tool**: Automatically generates schemas from examples
3. **Documentation Generator**: Creates markdown documentation with curl examples

## Validation Process

### Prerequisites

Install the Anypoint CLI tool and API project plugin:

```bash
npm install -g anypoint-cli-v4
anypoint-cli-v4 plugins:install anypoint-cli-api-project-plugin
```

For the schema inference tool, also install:
```bash
pip install pyyaml
```

### Automated Validation

Validation should be performed in **two passes** to ensure both syntax correctness and AI-agent compliance:

#### Pass 1: Basic OAS Format Validation

First, validate that the OAS file is syntactically correct:

```bash
anypoint-cli-v4 api-project validate --json --location=./path/to/folder/with/oas
```

This validates:
- OpenAPI specification structure and syntax
- Valid YAML/JSON format
- Required OAS fields present
- Basic schema correctness

**Important**: Only proceed to Pass 2 if Pass 1 succeeds. Fix any syntax errors first.

#### Pass 2: Full Compliance Validation

After Pass 1 succeeds, validate against all AI-agent-friendly rules:

```bash
anypoint-cli-v4 api-project validate --json --location=./path/to/folder/with/oas --local-ruleset skills/api-spec-validator/scripts/ruleset.yaml
```

This validates:
1. Descriptive operation IDs (Rule 2)
2. Comprehensive descriptions with context (Rule 3)
3. Examples in requests and responses (Rule 4)
4. Type documentation for all properties (Rule 5)
5. Output types fully documented (Rule 6)
6. No naked strings - enums required (Rule 7)
7. Required fields explicitly listed (Rule 8)

The tool will:
- Parse the OAS file
- Check all validation rules
- Generate a detailed report with violations
- Exit with status code 0 (pass) or 1 (fail)

### Complete Validation Workflow

The recommended workflow for validating an API specification:

1. **Check format**: Ensure spec is OAS (not RAML) - convert if needed
2. **Pass 1 - Basic validation**: Run `anypoint-cli-v4 api-project validate  --json --location=./path`
3. **Fix syntax errors**: Address any errors from Pass 1 before continuing
4. **Pass 2 - Compliance validation**: Run with `--local-ruleset skills/api-spec-validator/scripts/ruleset.yaml`
5. **Review violations**: Check the detailed report for rule violations
6. **Fix violations**: Update spec to address each violation
7. **Re-run Pass 2**: Verify all violations are resolved

### Manual Review Checklist

When reviewing specs manually:
1. Check if spec is in RAML format - if so, translate to OAS first
2. Check each endpoint has `operationId`, `description`, and examples
3. Verify operation IDs are descriptive (not generic)
4. Look for legacy field names requiring mapping explanations
5. Identify slow/rate-limited endpoints needing warnings
6. Check for cryptic paths needing AI aliases in `summary`
7. Check 400 responses for error codes - add recovery instructions
8. Ensure all string fields with limited options use `enum`
9. Verify all schemas have explicit `required` arrays
10. Confirm all properties have meaningful descriptions

### Running Validation with Claude

Claude will automatically run both validation passes when you ask:

```
"Validate my API spec at path/to/api-spec.yaml"
"Check this OpenAPI specification for AI-agent compliance"
"Review my OAS file at specs/my-api.yaml"
```

Claude will:
1. Run Pass 1 (basic OAS validation)
2. If Pass 1 succeeds, run Pass 2 (compliance validation)
3. Provide a summary of violations and recommendations

## Schema Inference Tool

When an API specification has examples but missing schemas, use the schema inference tool to automatically generate schemas from the examples.

### When to Use

Use this tool when:
- Endpoints have `examples` or `example` fields but no `schema` defined
- You want to quickly bootstrap schemas from sample data
- Converting from formats that don't require explicit schemas

### Running Schema Inference

#### Preview Changes (Dry Run)

```bash
python3 skills/api-spec-validator/scripts/infer_schemas.py path/to/spec.yaml --dry-run
```

This shows what schemas would be added without modifying the file.

#### Apply Changes

```bash
python3 skills/api-spec-validator/scripts/infer_schemas.py path/to/spec.yaml
```

This will:
1. Create a backup file (`spec.yaml.backup`)
2. Infer schemas from all examples in requests and responses
3. Add schemas where they are missing
4. Preserve existing schemas (never overwrites)

### What It Does

The tool:
- **Detects types**: Automatically determines `string`, `number`, `integer`, `boolean`, `array`, `object`, `null`
- **Handles nested objects**: Recursively processes complex structures
- **Infers formats**: Detects `email`, `uri`, `date` formats from string patterns
- **Sets required fields**: Marks all fields as required (conservative approach)
- **Adds descriptions**: Includes placeholder descriptions that need to be updated

### Example

**Before:**
```yaml
paths:
  /users:
    post:
      requestBody:
        content:
          application/json:
            examples:
              createUser:
                value:
                  name: "John Doe"
                  email: "john@example.com"
                  age: 30
      responses:
        '200':
          description: Success
          content:
            application/json:
              example:
                id: "123"
                status: "active"
```

**After running inference:**
```yaml
paths:
  /users:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [name, email, age]
              properties:
                name:
                  type: string
                  description: "Auto-generated from example. TODO: Add meaningful description for 'name'"
                email:
                  type: string
                  format: email
                  description: "Auto-generated from example. TODO: Add meaningful description for 'email'"
                age:
                  type: integer
                  description: "Auto-generated from example. TODO: Add meaningful description for 'age'"
            examples:
              createUser:
                value:
                  name: "John Doe"
                  email: "john@example.com"
                  age: 30
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                required: [id, status]
                properties:
                  id:
                    type: string
                    description: "Auto-generated from example. TODO: Add meaningful description for 'id'"
                  status:
                    type: string
                    description: "Auto-generated from example. TODO: Add meaningful description for 'status'"
              example:
                id: "123"
                status: "active"
```

### Post-Inference Steps

After running the inference tool:

1. **Review generated schemas**: Check that inferred types are correct
2. **Update descriptions**: Replace all "TODO" placeholders with meaningful descriptions
3. **Add enums**: If a field has limited options, add an `enum` array (see Rule 7)
4. **Refine required fields**: Adjust the `required` array if some fields are optional
5. **Add constraints**: Add `minLength`, `maxLength`, `minimum`, `maximum`, etc. as needed
6. **Run validation**: Use the validation tool to check for remaining issues

### Using with Claude

Ask Claude to infer schemas:

```
"Infer schemas from examples in my API spec at path/to/spec.yaml"
"Generate schemas from the examples in specs/my-api.yaml"
"My spec has examples but no schemas - can you add them?"
```

## Documentation Generator

Generates markdown documentation from your OpenAPI Specification, creating multiple pages with curl command examples for each endpoint.

### When to Use

Use this tool when:
- You need to create developer documentation from your API spec
- You want to provide curl examples for each endpoint
- You need human-readable documentation separate from the OAS file
- You're building a documentation website or wiki

### Running Documentation Generator

```bash
python3 skills/api-spec-validator/scripts/generate_docs.py path/to/spec.yaml [output-dir]
```

Default output directory is `./docs` if not specified.

### What Gets Generated

The tool creates:

1. **README.md** (Overview page):
   - API title, version, and description
   - List of base URLs/servers
   - Table of contents organized by tags
   - Links to all endpoint pages

2. **Individual endpoint pages** (one per operation):
   - HTTP method and path
   - Description and summary
   - Parameters table (path, query, header)
   - Request body details
   - **Curl command examples** with realistic values
   - Response examples with status codes
   - Response codes table

### Example

```bash
# Generate docs to default ./docs directory
python3 skills/api-spec-validator/scripts/generate_docs.py api-spec.yaml

# Generate docs to custom directory
python3 skills/api-spec-validator/scripts/generate_docs.py api-spec.yaml ./documentation
```

**Output:**
```
Generating API documentation from api-spec.yaml...

Generating overview page: README.md
Generating endpoint page: createUser.md
Generating endpoint page: getUserById.md
Generating endpoint page: listOrders.md

✓ Generated documentation for 3 endpoints
✓ Output directory: ./docs

View the documentation:
  - Overview: ./docs/README.md
```

### Curl Examples

The tool automatically generates curl commands with:
- Correct HTTP method
- Base URL from servers configuration
- Path parameters replaced with example values
- Query parameters included
- Headers included
- Request body with proper JSON formatting
- Multiple examples if the spec provides them

**Example generated curl command:**
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

### Using with Claude

Ask Claude to generate documentation:

```
"Generate markdown documentation from my API spec at path/to/spec.yaml"
"Create API docs with curl examples from specs/my-api.yaml"
"Generate developer documentation for my OpenAPI spec"
```

### Organizing Documentation

The generated documentation can be:
- Committed to your repository in a `docs/` folder
- Published to GitHub Pages or similar
- Imported into a wiki or documentation platform
- Shared with API consumers as standalone files

Each endpoint gets its own file, making it easy to:
- Link directly to specific endpoints
- Update individual endpoints without touching others
- Organize in folders by tag/category if needed
```

## Best Practices

### Creating AI-Friendly Specs

When authoring or reviewing specs, optimize for AI agent consumption:
- **Use OAS format**: Convert RAML specs to OAS for compatibility
- **Be explicit**: Don't assume the AI knows implicit conventions
- **Add context**: Explain business rules, state transitions, constraints
- **Warn proactively**: Surface gotchas (rate limits, slow endpoints, deprecated fields)
- **Map legacy fields**: Translate internal codes to human-readable meanings
- **Document error recovery**: Add recovery instructions for 400 responses with error codes
- **Use examples liberally**: Show don't tell - examples are worth a thousand words

### Common Issues to Fix

1. **RAML format**: Convert RAML specs to OAS before validation
2. **Generic operation IDs**: Replace `getData` with `getUserProfile`
3. **Missing enums**: Add enums for status codes, types, categories
4. **Undocumented fields**: Add descriptions explaining purpose and usage
5. **Missing required arrays**: Explicitly list which fields are mandatory
6. **Cryptic paths**: Add summary aliases for `/rpc/` or `/action/` style paths
7. **Undocumented 400 errors**: Add recovery instructions for error codes

## Output Format

When validating with `anypoint-cli-v4`, the tool provides a structured report:

```
Validating API specification...

✓ oas-only: Valid OpenAPI 3.0.2 format
✓ operation-examples: All operations have examples

⚠ Violations found:

1. operation-id-camel-case
   - GET /users: operationId 'get_data' must be in camelCase
   - Use descriptive names like 'getUserProfile' or 'calculateTaxRate'

2. no-naked-strings
   - POST /orders (request): Property 'status' must have enum
   - Avoid naked strings with no constraints

3. schema-required-block
   - POST /users: Schema must explicitly list required fields

Validation completed with 3 violations
```

When summarizing results for users, organize by rule type and provide actionable fixes.

## References

For detailed examples and guides:
- `references/example-good-spec.yaml` - Example of a fully compliant spec with all best practices
- `references/example-violations.yaml` - Common mistakes and how to fix them
- `references/raml-to-oas-guide.md` - Comprehensive guide for converting RAML specifications to OAS
