#!/bin/bash

set -e

HF_USERNAME="VashuTheGreat2"
SPACE_NAME="JOSAA_RANK_PREDICTOR"

echo "📁 Using Jenkins workspace..."
pwd
ls -la

echo "🤗 Checking HF CLI..."

# FIX PATH ISSUE FIRST (IMPORTANT)
export PATH="$PATH:/var/lib/jenkins/.local/bin"

if command -v hf &> /dev/null
then
    echo "✅ hf CLI already available"
else
    echo "❌ hf not found. Installing via pipx..."

    if ! command -v pipx &> /dev/null
    then
        sudo apt update
        sudo apt install -y pipx
    fi

    pipx install huggingface_hub || pipx install huggingface_hub --force

    # again fix PATH after install
    export PATH="$PATH:/var/lib/jenkins/.local/bin"
fi

echo "🔍 Verifying hf..."
which hf || echo "⚠️ hf still not found in PATH"
hf --help || true

echo "🔐 Authenticating to Hugging Face..."

if [ -z "$HF_TOKEN" ]; then
    echo "❌ HF_TOKEN not set in Jenkins credentials"
    exit 1
fi

hf auth login --token "$HF_TOKEN"

echo "📝 Writing README for HF Space..."

cat > README.md <<EOF
---
title: $SPACE_NAME
emoji: 🚀
colorFrom: pink
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# $SPACE_NAME

Auto deployed via Jenkins 🚀
EOF

echo "🚀 Creating HF Space (if not exists)..."

hf repo create "$SPACE_NAME" \
    --type space \
    --space-sdk docker \
    || echo "⚠️ Space already exists"

echo "📤 Pushing to Hugging Face..."

HF_REPO_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

if git remote | grep hf; then
    echo "✅ HF remote already exists"
else
    git remote add hf "$HF_REPO_URL"
fi

git add .
git commit -m "🚀 Auto deploy to HF Space" || echo "No changes to commit"

git push hf main

echo "🎉 DEPLOYMENT COMPLETE 🚀"
