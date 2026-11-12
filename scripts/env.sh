# Sourced by the run_P*.sh scripts. Loads paths from the repo's .env file.
# Sets: REPO, SIM, BENCH, RES, DATA

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$REPO/.env" ]; then
  echo "No .env file found. Run:  cp $REPO/.env.example $REPO/.env  and edit the paths." >&2
  exit 1
fi

set -a
. "$REPO/.env"
set +a

expand () { eval echo "$1"; }   # expands ~ and $HOME written inside .env
SIM=$(expand "$SIM")
BENCH=$(expand "$BENCH")
RES=$(expand "${RES:-$REPO/results}")
DATA=$(expand "${DATA:-$REPO/data}")

[ -x "$SIM" ] || { echo "SIM is not an executable file: $SIM (check .env)" >&2; exit 1; }
[ -d "$BENCH/Input" ] || { echo "BENCH has no Input/ folder: $BENCH (check .env)" >&2; exit 1; }
mkdir -p "$RES" "$DATA"
