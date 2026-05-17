#!/usr/bin/env bash
# Wrapper script to launch QGIS with RNA plugin JWT secret.

SECRET_FILE="${HOME}/.cache/rna-jwt-secret"

if [ ! -f "$SECRET_FILE" ]; then
    mkdir -p "$(dirname "$SECRET_FILE")"
    python3 -c "import secrets; print(secrets.token_hex(32))" > "$SECRET_FILE"
    chmod 600 "$SECRET_FILE"
fi

export RNA_JWT_SECRET
RNA_JWT_SECRET=$(cat "$SECRET_FILE")

exec qgis "$@"
