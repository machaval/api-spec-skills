# RAML to OAS Conversion Guide

## Overview

RAML (RESTful API Modeling Language) specifications should be converted to OpenAPI Specification (OAS) format for validation and to ensure broader tool compatibility.

## Conversion Tools

### Recommended Tools

1. **API Transformer** (Online)
   - URL: https://www.apimatic.io/transformer/
   - Supports RAML 1.0/0.8 to OAS 3.0

2. **RAML to OAS Converter (NPM)**
   ```bash
   npm install -g raml2obj oas-raml-converter
   oas-raml-converter --from RAML --to OAS30 input.raml > output.yaml
   ```

3. **oas-raml-converter-cli**
   ```bash
   npm install -g oas-raml-converter-cli
   raml-to-oas input.raml output.yaml
   ```

## Manual Conversion Mapping

### Basic Structure

**RAML:**
```yaml
#%RAML 1.0
title: My API
version: v1
baseUri: https://api.example.com/{version}
```

**OAS:**
```yaml
openapi: 3.0.2
info:
  title: My API
  version: v1
servers:
  - url: https://api.example.com/v1
```

### Resource/Path Conversion

**RAML:**
```yaml
/users:
  get:
    displayName: Get Users
    responses:
      200:
        body:
          application/json:
            type: User[]
```

**OAS:**
```yaml
paths:
  /users:
    get:
      operationId: getUsers
      summary: Get Users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

### Data Types Conversion

**RAML:**
```yaml
types:
  User:
    properties:
      id: integer
      name: string
      email:
        type: string
        required: true
```

**OAS:**
```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
      required:
        - email
```

### URI Parameters

**RAML:**
```yaml
/users/{userId}:
  uriParameters:
    userId:
      type: integer
      description: User ID
```

**OAS:**
```yaml
/users/{userId}:
  parameters:
    - name: userId
      in: path
      required: true
      schema:
        type: integer
      description: User ID
```

### Query Parameters

**RAML:**
```yaml
/users:
  get:
    queryParameters:
      limit:
        type: integer
        default: 10
      offset:
        type: integer
        default: 0
```

**OAS:**
```yaml
/users:
  get:
    parameters:
      - name: limit
        in: query
        schema:
          type: integer
          default: 10
      - name: offset
        in: query
        schema:
          type: integer
          default: 0
```

### Traits to OAS

RAML traits need to be manually applied in OAS. Common patterns:

**RAML Trait:**
```yaml
traits:
  pageable:
    queryParameters:
      page:
        type: integer
      size:
        type: integer
```

**Applied in OAS:** Duplicate the parameters in each endpoint or use `$ref` to a common parameter definition:

```yaml
components:
  parameters:
    PageParam:
      name: page
      in: query
      schema:
        type: integer
    SizeParam:
      name: size
      in: query
      schema:
        type: integer

paths:
  /users:
    get:
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/SizeParam'
```

## Post-Conversion Validation

After converting RAML to OAS, ensure:

1. **Add Operation IDs**: RAML `displayName` becomes `summary` - add proper `operationId`
2. **Add Examples**: RAML examples may not translate - manually add request/response examples
3. **Refine Descriptions**: Enhance descriptions with warnings, mappings, and context
4. **Add Enums**: Convert RAML type constraints to proper OAS enums
5. **Validate Required Fields**: Ensure all `required` arrays are explicit

## Common Conversion Issues

### Issue 1: Missing Operation IDs
**Problem:** RAML doesn't have operationId concept
**Solution:** Add descriptive operationIds after conversion (e.g., `getUserById`, `createOrder`)

### Issue 2: Traits Not Converted
**Problem:** RAML traits don't have direct OAS equivalent
**Solution:** Manually apply trait parameters to each endpoint or use `$ref`

### Issue 3: Resource Types Lost
**Problem:** RAML resourceTypes are not preserved
**Solution:** Use OAS `$ref` for common schemas and parameters

### Issue 4: Annotations Lost
**Problem:** RAML annotations may not translate
**Solution:** Convert annotations to OAS extensions (x-*) or descriptions

### Issue 5: Includes Not Resolved
**Problem:** RAML `!include` directives may not resolve
**Solution:** Use conversion tools that support includes or manually merge files

## Best Practices

1. **Use Automated Tools First**: Start with automated conversion tools
2. **Manual Review Required**: Always manually review converted specs
3. **Enhance Descriptions**: Add AI-friendly context post-conversion
4. **Test Endpoints**: Validate converted spec against actual API behavior
5. **Run Validator**: Use the api-spec-validator after conversion to catch issues

## Example Workflow

```bash
# 1. Convert RAML to OAS
raml-to-oas api-spec.raml api-spec.yaml

# 2. Manual enhancement
# - Add operationIds
# - Add examples
# - Add recovery instructions for 400 errors
# - Add enums where appropriate

# 3. Validate
python skills/api-spec-validator/scripts/validate_spec.py api-spec.yaml

# 4. Iterate based on validation report
```

## References

- [RAML Specification](https://github.com/raml-org/raml-spec)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [RAML to OAS Converter](https://github.com/stoplightio/http-spec/tree/master/packages/oas-raml-converter)
