#!/bin/bash -e
if [ -z "$ALLOW" ]; then
    allow="--allow 10.0.0.1/16"
else
    allow=$ALLOW
fi

append_params=""

if [ -n "$JOBS" ]; then
    append_params="$append_params --jobs $JOBS"
fi

distccd $allow --daemon --verbose --no-detach $append_params
