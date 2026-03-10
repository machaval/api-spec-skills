---
name: api-spec-validator
description: This skill should be used when the user asks to "validate API spec", "check OpenAPI spec", "lint OAS", "review API specification", "convert RAML to OAS", or mentions validating, checking, or reviewing OpenAPI/OAS/Swagger/RAML specifications against best practices.
metadata: 
  version: 1.0.0
  author: "Mariano de Achaval"
---

# API Spec Validator

This skill validates OpenAPI Specification (OAS) files against a comprehensive set of rules designed to ensure API specifications are AI-agent-friendly and production-ready.

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

**RAML Translation**: If the API specification is written in RAML format, translate it to OAS before validation. Use conversion tools or manual translation to ensure all RAML features are properly represented in OAS format.

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

## Validation Process

### Automated Validation

Use the bundled Python validation script for programmatic checking:

```bash
python skills/api-spec-validator/scripts/validate_spec.py <path-to-spec.yaml>
```

The script will:
1. Parse the OAS file
2. Check all validation rules
3. Generate a detailed report with violations
4. Exit with status code 0 (pass) or 1 (fail)

### Manual Review

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

When validating, provide a report structured as:

```markdown
# API Spec Validation Report

## Summary
- Total Endpoints: X
- Violations Found: Y
- Pass Rate: Z%

## Violations

### Rule 2: Missing/Generic Operation IDs
- GET /users/{id} - Missing operationId
- POST /data - operationId "post_data" is too generic

### Rule 7: Naked Strings
- /orders POST request.status - should use enum instead of string

### Rule 8: Missing Required Fields
- /users POST - schema missing required array

## Passed
- Rule 1: Valid OAS 3.0.2 format ✓
- Rule 4: All endpoints have examples ✓
```

## References

For detailed examples and guides:
- `references/example-good-spec.yaml` - Example of a fully compliant spec with all best practices
- `references/example-violations.yaml` - Common mistakes and how to fix them
- `references/raml-to-oas-guide.md` - Comprehensive guide for converting RAML specifications to OAS
