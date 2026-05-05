# MCP-Style Tools

Tools implement a common base class with:

- `name`
- `description`
- `input_schema`
- `output_schema`
- `execute`

The platform exposes discovery at `GET /tools` and execution at `POST /tools/{tool_name}/execute`. This gives an MCP-like contract without requiring an external MCP server for the first version.
