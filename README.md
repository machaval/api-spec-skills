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
/plugin marketplace add machaval/api-design-skills
```

2. Install the skills you need:
```bash
/plugin install api-spec-validator@api-design-skills
```

Alternatively, clone this repository and reference the skills directly in your project.

### Manual Installation

Clone the repository to your local machine:
```bash
git clone https://github.com/machaval/api-design-skills.git
cd api-design-skills
```

Install Python dependencies for the validation script:
```bash
pip install pyyaml
```

## Usage

### Using with Claude Code

Once installed, simply mention the skill in your requests to Claude:

> "Use the api-spec-validator skill to validate my OpenAPI spec at specs/my-api.yaml"

> "Check this API specification for AI-agent friendliness"

> "Validate the OAS file and tell me what needs to be fixed"

### Command-Line Usage

Run the validation script directly:

```bash
python skills/api-spec-validator/scripts/validate_spec.py path/to/your-spec.yaml
```

Example output:
```
======================================================================
API SPEC VALIDATION REPORT
======================================================================

Spec: api-spec.yaml
Total Endpoints: 5
Violations Found: 3
Pass Rate: 85.7%

----------------------------------------------------------------------
VIOLATIONS
----------------------------------------------------------------------

### Rule 2: Operation ID Quality
    (1 violation)
  ❌ GET /users
     operationId 'get_data' is too generic

### Rule 7: No Naked Strings
    (2 violations)
  ⚠️  POST /orders (request)
     Property 'status' missing enum

======================================================================
✅ VALIDATION PASSED (warnings only)
======================================================================
```

## Repository Structure

```
api-design-skills/
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
You: Validate my API spec at specs/orders-api.yaml

Claude: I'll use the api-spec-validator skill to check your specification.
[Runs validation and provides detailed report with violations and fixes]
```

### Command Line

```bash
python skills/api-spec-validator/scripts/validate_spec.py specs/orders-api.yaml
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
2. Add validation logic to `validate_spec.py`
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
