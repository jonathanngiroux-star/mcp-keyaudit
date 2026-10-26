#!/usr/bin/env python3
"""MCP server for keyaudit - Key Management Consulting"""

import json
import os
from datetime import datetime
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("mcp-keyaudit")

# Simulated data
CEREMONIES = {
    "ceremony-001": {
        "id": "ceremony-001",
        "name": "Quarterly Key Rotation Q4 2024",
        "type": "key_rotation",
        "status": "completed",
        "participants": ["alice@company.com", "bob@company.com", "carol@company.com"],
        "threshold": 2,
        "scheduled_at": "2024-12-15T10:00:00",
        "completed_at": "2024-12-15T10:45:00",
        "artifacts": ["attestation-001.pdf", "key-manifest-001.json"]
    },
    "ceremony-002": {
        "id": "ceremony-002",
        "name": "Emergency Key Recovery",
        "type": "emergency_recovery",
        "status": "in_progress",
        "participants": ["alice@company.com", "dave@company.com"],
        "threshold": 2,
        "scheduled_at": "2024-12-20T14:00:00",
        "completed_at": None,
        "artifacts": []
    }
}

BACKUPS = {
    "backup-001": {
        "id": "backup-001",
        "name": "HSM Backup - Q4 2024",
        "type": "hsm_backup",
        "status": "verified",
        "location": "offsite-vault-a",
        "created_at": "2024-10-01T10:00:00",
        "verified_at": "2024-10-01T10:30:00",
        "checksum": "sha256:abc123...",
        "size_bytes": 2048576
    },
    "backup-002": {
        "id": "backup-002",
        "name": "Paper Wallet Backup - Treasury",
        "type": "paper_wallet",
        "status": "verified",
        "location": "safe-deposit-box-b",
        "created_at": "2024-09-15T09:00:00",
        "verified_at": "2024-09-15T09:15:00",
        "checksum": "sha256:def456...",
        "size_bytes": 1024
    }
}

HARDWARE = {
    "hsm-001": {
        "id": "hsm-001",
        "name": "HSM Primary",
        "model": "nCipher nShield Connect XC",
        "serial": "NC-12345",
        "firmware": "12.71.0",
        "status": "operational",
        "location": "datacenter-a-rack-12",
        "last_audit": "2024-11-15",
        "certifications": ["FIPS 140-2 Level 3", "Common Criteria EAL4+"]
    },
    "hsm-002": {
        "id": "hsm-002",
        "name": "HSM Backup",
        "model": "Thales Luna Network HSM 7",
        "serial": "TH-67890",
        "firmware": "7.7.1",
        "status": "operational",
        "location": "datacenter-b-rack-05",
        "last_audit": "2024-11-20",
        "certifications": ["FIPS 140-2 Level 3", "Common Criteria EAL4+"]
    }
}

app = Server("mcp-keyaudit")

TOOLS = [
    Tool(
        name="audit_key_ceremony",
        description="Audit a key ceremony - verify participants, threshold, and artifacts",
        inputSchema={
            "type": "object",
            "properties": {
                "ceremony_id": {"type": "string", "description": "Ceremony identifier"},
                "verify_artifacts": {"type": "boolean", "default": True, "description": "Verify artifact integrity"}
            },
            "required": ["ceremony_id"]
        }
    ),
    Tool(
        name="get_backup_status",
        description="Get backup status and verification status",
        inputSchema={
            "type": "object",
            "properties": {
                "backup_id": {"type": "string", "description": "Backup identifier (optional, returns all if not provided)"}
            }
        }
    ),
    Tool(
        name="review_hardware_config",
        description="Review hardware security module configuration and audit status",
        inputSchema={
            "type": "object",
            "properties": {
                "hsm_id": {"type": "string", "description": "HSM identifier (optional, returns all if not provided)"},
                "check_firmware": {"type": "boolean", "default": True, "description": "Check firmware version"}
            }
        }
    )
]

app = Server("mcp-keyaudit")

@app.list_tools()
async def list_tools():
    return TOOLS

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "audit_key_ceremony":
        ceremony_id = arguments.get("ceremony_id")
        verify_artifacts = arguments.get("verify_artifacts", True)
        
        ceremony = CEREMONIES.get(ceremony_id)
        if not ceremony:
            return [TextContent(type="text", text=json.dumps({"error": f"Ceremony not found: {ceremony_id}"}))]
        
        # Audit checks
        checks = {
            "participants_valid": len(ceremony["participants"]) >= ceremony["threshold"],
            "threshold_met": len(ceremony["participants"]) >= ceremony["threshold"],
            "artifacts_present": len(ceremony["artifacts"]) > 0,
            "timing": "on_schedule" if ceremony["completed_at"] else "in_progress"
        }
        
        artifact_verification = {}
        if verify_artifacts:
            for artifact in ceremony["artifacts"]:
                artifact_verification[artifact] = {"verified": True, "checksum_valid": True}
        
        result = {
            "status": "ok",
            "tool": "audit_key_ceremony",
            "ceremony_id": ceremony_id,
            "ceremony_name": ceremony["name"],
            "ceremony_type": ceremony["type"],
            "status": ceremony["status"],
            "checks": checks,
            "artifact_verification": artifact_verification if verify_artifacts else "skipped",
            "audited_at": datetime.now().isoformat()
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "get_backup_status":
        backup_id = arguments.get("backup_id")
        
        if backup_id:
            backup = BACKUPS.get(backup_id)
            if not backup:
                return [TextContent(type="text", text=json.dumps({"error": f"Backup not found: {backup_id}"}))]
            result = {"status": "ok", "tool": "get_backup_status", "backup": backup}
        else:
            result = {"status": "ok", "tool": "get_backup_status", "backups": list(BACKUPS.values())}
        
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "review_hardware_config":
        hsm_id = arguments.get("hsm_id")
        check_firmware = arguments.get("check_firmware", True)
        
        if hsm_id:
            hsm = HARDWARE.get(hsm_id)
            if not hsm:
                return [TextContent(type="text", text=json.dumps({"error": f"HSM not found: {hsm_id}"}))]
            
            result = {
                "status": "ok",
                "tool": "review_hardware_config",
                "hsm": hsm,
                "firmware_check": {"current": hsm["firmware"], "latest_available": "12.71.0", "update_available": hsm["firmware"] != "12.71.0"} if check_firmware else "skipped"
            }
        else:
            result = {
                "status": "ok",
                "tool": "review_hardware_config",
                "hsms": list(HARDWARE.values()),
                "total_count": len(HARDWARE),
                "firmware_summary": {h["id"]: h["firmware"] for h in HARDWARE.values()}
            }
        
        if check_firmware:
            for hsm in HARDWARE.values():
                if hsm["firmware"] != "12.71.0":
                    result.setdefault("alerts", []).append(f"HSM {hsm['id']} firmware outdated: {hsm['firmware']}")
        
        return [TextContent(type="text", text=json.dumps(result))]
    
    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def serve():
        reader, writer = await stdio_server()
        await app.run(reader, writer)
    
    asyncio.run(serve())