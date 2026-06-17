#!/bin/bash
# LLM Tracker daily refresh.
# - Re-fetches OpenRouter live data (pricing, context, new models)
# - Re-merges with our curated specialties & hosting
# - Copies the merged file into static/ (Tailscale Funnel chokes on symlinks)
# - Rebuilds the inlined single-file index.html
# - Updates sync_state.json so the UI can show last sync time

set -euo pipefail
PROJECT="/home/ryancalpin/workspace/llm-tracker"
LOG="$PROJECT/logs/refresh.log"
STATE="$PROJECT/static/sync_state.json"
mkdir -p "$PROJECT/logs"

# Detect trigger: "auto" if run by systemd timer (INVOCATION_ID set), "manual" otherwise
TRIGGER="${LLM_TRACKER_SYNC_TRIGGER:-auto}"
NOW="$(date -Iseconds)"

# Initialize state file if missing
if [ ! -f "$STATE" ]; then
  echo '{"last_sync_at":null,"last_sync_status":"never","syncing":false,"history":[]}' > "$STATE"
fi

# Mark sync as started
python3 -c "
import json
from pathlib import Path
p = Path('$STATE')
state = json.loads(p.read_text()) if p.exists() else {'history': []}
state['syncing'] = True
state['sync_started_at'] = '$NOW'
state['sync_trigger'] = '$TRIGGER'
p.write_text(json.dumps(state, indent=2))
"

{
  echo "=== $NOW ($TRIGGER) ==="
  python3 "$PROJECT/scripts/fetch_openrouter.py" 2>&1
  python3 "$PROJECT/scripts/fetch_specialties.py" 2>&1
  python3 "$PROJECT/scripts/merge.py" 2>&1
  # Real file copy into static/ so Tailscale Funnel serves it reliably
  cp -f "$PROJECT/data/models.json" "$PROJECT/static/models.json"
  # Rebuild self-contained single-file index.html
  python3 "$PROJECT/scripts/build_inline.py" 2>&1
  cp -f "$PROJECT/static/index-inline.html" "$PROJECT/static/index.html"
  echo "OK"
} >> "$LOG" 2>&1

EXIT_CODE=$?

# Mark sync as completed
python3 -c "
import json
from pathlib import Path
from datetime import datetime, timezone
p = Path('$STATE')
state = json.loads(p.read_text()) if p.exists() else {'history': []}
now = datetime.now(timezone.utc).isoformat()
state['syncing'] = False
state['last_sync_at'] = now
state['last_sync_status'] = 'ok' if $EXIT_CODE == 0 else 'error'
history = state.get('history', [])
history.append({'at': now, 'status': state['last_sync_status'], 'trigger': '$TRIGGER'})
state['history'] = history[-20:]
p.write_text(json.dumps(state, indent=2))
"

exit $EXIT_CODE
