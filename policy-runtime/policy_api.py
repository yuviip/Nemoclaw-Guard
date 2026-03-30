from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import subprocess
import json

app = FastAPI()
POLICY_CMD = ["/opt/nemoclaw/bin/policy_decide.sh"]
APPROVAL_RESOLVE_CMD = ["/opt/nemoclaw/bin/approval_resolve.py"]


def run_json_command(cmd, payload, timeout=20):
    try:
        proc = subprocess.run(
            cmd,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail=f"{cmd[0]} timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{cmd[0]} launch failed: {e}")

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if proc.returncode != 0:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "command_failed",
                "command": cmd[0],
                "returncode": proc.returncode,
                "stderr": stderr,
                "stdout": stdout,
            },
        )

    try:
        data = json.loads(stdout)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "invalid_command_output",
                "command": cmd[0],
                "stdout": stdout,
                "stderr": stderr,
            },
        )

    if isinstance(data, dict) and "ok" not in data:
        data["ok"] = True

    return JSONResponse(content=data)


@app.get("/health")
def health():
    return JSONResponse(content={"ok": True, "service": "policy-api"})


@app.post("/decide")
async def decide(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    return run_json_command(POLICY_CMD, payload, timeout=20)


@app.post("/approval/resolve")
async def approval_resolve(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    text = payload.get("text")
    request_session = payload.get("request_session")

    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="text must be a string")

    if not isinstance(request_session, dict):
        raise HTTPException(status_code=400, detail="request_session must be an object")

    return run_json_command(
        APPROVAL_RESOLVE_CMD,
        {
            "text": text,
            "request_session": request_session,
        },
        timeout=30,
    )
