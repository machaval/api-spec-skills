# RAML to OAS Conversion Guide

## Overview

RAML (RESTful API Modeling Language) specifications should be converted to OpenAPI Specification (OAS) format for validation and to ensure broader tool compatibility.

## Recommended tools

1. Anypoint CLI

```bash
npm install -g anypoint-cli-v4
anypoint-cli-v4 plugins:install anypoint-cli-api-project-plugin
```

##  Validation

Ensure each OAS to:

1. **Add Operation IDs**: RAML `displayName` becomes `summary` - add proper `operationId`
2. **Add Examples**: RAML examples may not translate - manually add request/response examples
3. **Refine Descriptions**: Enhance descriptions with warnings, mappings, and context
4. **Add Enums**: Convert RAML type constraints to proper OAS enums
5. **Validate Required Fields**: Ensure all `required` arrays are explicit

## Common Conversion Issues

### Issue 1: Missing Operation IDs
**Problem:** RAML doesn't have operationId concept
**Solution:** Add descriptive operationIds after conversion (e.g., `getUserById`, `createOrder`) and make them unique

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


# 1. Manual enhancement
# - Add operationIds
# - Add examples
# - Add recovery instructions for 400 errors
# - Add enums where appropriate

# 2. Validate is a valid oas
anypoint-cli-v4 api-project validate  --location=./pathToFolderWhereTheOASIs  

# 3. Validate is compliant with the rules

anypoint-cli-v4 api-project validate  --location=./pathToFolderWhereTheOASIs  --local-ruleset skills/api-spec-validator/scripts/ruleset.yaml

# 4. Iterate based on validation report
```

## References

- [RAML Specification](https://github.com/raml-org/raml-spec)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [RAML to OAS Converter](https://github.com/stoplightio/http-spec/tree/master/packages/oas-raml-converter)
