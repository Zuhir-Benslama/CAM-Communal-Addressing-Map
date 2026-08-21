#!/usr/bin/env bash
# Wrapper script to launch QGIS with CAM plugin JWT secret.

SECRET_FILE="${HOME}/.cache/cam-jwt-secret"

if [ ! -f "$SECRET_FILE" ]; then
    mkdir -p "$(dirname "$SECRET_FILE")"
    python3 -c "import secrets; print(secrets.token_hex(32))" > "$SECRET_FILE"
    chmod 600 "$SECRET_FILE"
fi

export CAM_JWT_SECRET
CAM_JWT_SECRET=$(cat "$SECRET_FILE")

exec qgis "$@"
