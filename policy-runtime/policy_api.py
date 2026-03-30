from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import subprocess
import json

app = FastAPI()
POLICY_CMD = ["/opt/nemoclaw/bin/policy_decide.sh"]

@app.get("/health")
def health():
    return JSONResponse(content={"ok": True, "service": "policy-api"})

@app.post("/decide")
async def decide(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        proc = subprocess.run(
            POLICY_CMD,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="policy_decide timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"policy_decide launch failed: {e}")

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if proc.returncode != 0:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "policy_decide_failed",
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
                "error": "invalid_policy_output",
                "stdout": stdout,
                "stderr": stderr,
            },
        )

    data["ok"] = True
    return JSONResponse(content=data)
