#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_BIN="/opt/openclaw/bin"
CANONICAL_BIN="/opt/nemoclaw-guard/runtime/bin"
TS="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$OPENCLAW_BIN"

install_shim() {
  local name="$1"
  local target="$OPENCLAW_BIN/$name"
  local canonical="$CANONICAL_BIN/$name"

  [ -f "$canonical" ] || { echo "ERROR: missing canonical wrapper $canonical"; exit 1; }

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    cp -a "$target" "${target}.pre_shim_${TS}"
    echo "backup_created=${target}.pre_shim_${TS}"
  fi

  cat > "$target" <<SHIM
#!/usr/bin/env bash
set -euo pipefail
exec "$canonical" "\$@"
SHIM

  chmod 755 "$target"
  echo "shim_installed=$target -> $canonical"
}

install_shim guarded_git_push.sh
install_shim guarded_file_delete.sh
install_shim guarded_ha_call.sh
install_shim guarded_systemctl.sh
install_shim guarded_docker_restart.sh
