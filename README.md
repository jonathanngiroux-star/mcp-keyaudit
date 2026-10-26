# mcp-keyaudit

MCP server for key management consulting - audit key ceremonies, backup status, hardware config review.

## Tools

### audit_key_ceremony
Audit a key ceremony - verify participants, threshold, and artifacts.

**Parameters:**
- `ceremony_id` (string, required): Ceremony identifier
- `verify_artifacts` (boolean, optional): Verify artifact integrity (default: true)

### get_backup_status
Get backup status and verification status.

**Parameters:**
- `backup_id` (string, optional): Backup identifier (optional, returns all if not provided)

### review_hardware_config
Review hardware security module configuration and audit status.

**Parameters:**
- `hsm_id` (string, optional): HSM identifier (optional, returns all if not provided)
- `check_firmware` (boolean, optional): Check firmware version (default: true)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Connecting to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "keyaudit": {
      "command": "python",
      "args": ["/path/to/mcp-keyaudit/main.py"],
      "cwd": "/path/to/mcp-keyaudit"
    }
  }
}
```

## License

MIT