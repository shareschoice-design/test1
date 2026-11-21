#!/bin/bash
# usage: render_batch.sh <scratch_dir> name1 name2 ...   (renders shorts/<name> from footage/dvids, 2 at a time)
S=$1; shift
cd "$(dirname "$0")/.."
printf "%s\n" "$@" | xargs -P 2 -I{} sh -c "VOICE_DIR=$S/tts PIPER_MODEL=$S/tts/en_US-ryan-high.onnx LS=0.95 python3 shorts_tool/build_fast.py shorts/{} ${FOOT:-footage/dvids} $S/work_{} > $S/log_{}.txt 2>&1 && echo 'done {}' || echo 'FAIL {}'"
