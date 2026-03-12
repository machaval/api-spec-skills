# API Design Skills

A collection of reusable Claude skills for validating and improving API specifications. These skills help ensure your APIs are production-ready, well-documented, and optimized for AI agent consumption.

## What This Repository Contains

This repository provides **Claude skills for API design and validation** — specialized instructions and tools that Claude loads dynamically to help you create better API specifications that work seamlessly with AI agents.

**Key Purpose:** Help teams create API specifications that are:
- Complete and well-documented
- AI-agent-friendly
- Following industry best practices
- Production-ready with proper error handling and examples

## Available Skills

### API Spec Validator

Validates OpenAPI Specification (OAS) files against comprehensive rules to ensure APIs are AI-agent-friendly and production-ready.

**Features:**
- Validates OAS 3.0/3.1 and Swagger 2.0 formats
- Converts RAML specifications to OAS
- Checks for descriptive operation IDs and comprehensive descriptions
- Ensures proper examples, enums, and required field documentation
- Validates error response documentation with recovery instructions
- Provides detailed violation reports

**Learn more:** [skills/api-spec-validator/README.md](skills/api-spec-validator/README.md)

## Installation

### Using with Claude Code

1. Register this repository as a marketplace:
```bash
/plugin marketplace add machaval/api-spec-skills
```

2. Install the skills you need:
```bash
/plugin install api-spec-validator@api-spec-skills
```

Alternatively, clone this repository and reference the skills directly in your project.

### Manual Installation

Clone the repository to your local machine:
```bash
git clone https://github.com/machaval/api-spec-skills.git
cd api-spec-skills
```

Install the Anypoint CLI tool and API project plugin:
```bash
npm install -g anypoint-cli-v4
anypoint-cli-v4 plugins:install anypoint-cli-api-project-plugin
```

## Usage

### Using with Claude Code

Once installed, simply mention the skill in your requests to Claude:

> "Use the api-spec-validator skill to validate my OpenAPI spec at specs/my-api.yaml"

> "Check this API specification for AI-agent friendliness"

> "Validate the OAS file and tell me what needs to be fixed"

### Command-Line Usage

#### Basic OAS Format Validation

Validate that the OAS file is syntactically correct:

```bash
anypoint-cli-v4 api-project validate --location=./path/to/folder/with/oas
```

#### Full Compliance Validation

Validate against all AI-agent-friendly rules:

```bash
anypoint-cli-v4 api-project validate --location=./path/to/folder/with/oas --local-ruleset skills/api-spec-validator/scripts/ruleset.yaml
```

Example output:
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

## Repository Structure

```
api-spec-skills/
├── skills/
│   └── api-spec-validator/       # API validation skill
│       ├── SKILL.md              # Skill definition for Claude
│       ├── README.md             # Detailed documentation
│       ├── scripts/              # Validation scripts
│       └── references/           # Example specs and guides
├── scripts/                      # Utility scripts
├── README.md                     # This file
└── .vscode/                      # VS Code settings
```

## Example: Validating an API Spec

### With Claude Code

```
You: Validate my API spec at specs/orders-api/

Claude: I'll use the api-spec-validator skill to check your specification.
[Runs validation and provides detailed report with violations and fixes]
```

### Command Line

Basic validation:
```bash
anypoint-cli-v4 api-project validate --location=./specs/orders-api
```

Full compliance validation:
```bash
anypoint-cli-v4 api-project validate --location=./specs/orders-api --local-ruleset skills/api-spec-validator/scripts/ruleset.yaml
```

## Integration with CI/CD

Integrate the validator into your CI/CD pipeline:

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

## Why API Design Skills Matter

AI agents need well-structured, comprehensive API specifications to effectively interact with your APIs. Common issues that break AI agent workflows include:

- Generic operation IDs that don't convey intent
- Missing examples that leave agents guessing
- Undocumented error codes without recovery instructions
- Cryptic legacy field names without context
- Missing enums that force string guessing
- Ambiguous required vs optional fields

This skills repository helps you avoid these pitfalls and create APIs that work seamlessly with AI agents.

## Contributing

Contributions are welcome! To add new validation rules or skills:

1. Fork the repository
2. Create a new branch for your feature
3. Add your skill or enhancement
4. Test thoroughly with example specs
5. Submit a pull request

For API Spec Validator improvements:
1. Update `skills/api-spec-validator/SKILL.md` with new rules
2. Add validation logic to `ruleset.yaml` (AMF Validation Profile format)
3. Add examples to reference files
4. Update documentation

## License

This project is provided for demonstration and educational purposes. See LICENSE file for details.

## Resources

- [OpenAPI Specification](https://swagger.io/specification/)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Claude Agent Skills Specification](https://github.com/anthropics/skills)

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
