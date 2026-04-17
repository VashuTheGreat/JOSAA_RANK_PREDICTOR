#!/bin/bash

set -e

HF_USERNAME="VashuTheGreat2"
SPACE_NAME="JOSAA_RANK_PREDICTOR"

echo "📁 Using Jenkins workspace..."
pwd
ls -la

echo "🤗 Checking HF CLI..."

if command -v hf &> /dev/null
then
    echo "✅ hf CLI already installed"
else
    echo "❌ hf not found. Installing via pipx..."

    if ! command -v pipx &> /dev/null
    then
        sudo apt update
        sudo apt install -y pipx
        pipx ensurepath
    fi

    pipx install huggingface_hub
fi

echo "🔐 Login to HF..."

if [ -z "$HF_TOKEN" ]; then
    echo "❌ HF_TOKEN not set!"
    exit 1
fi

hf auth login --token $HF_TOKEN

echo "📝 Creating README for Docker Space..."

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

Docker-based Hugging Face Space 🚀
EOF

echo "🚀 Creating HF Space (Docker)..."

hf repo create $SPACE_NAME \
    --type space \
    --space-sdk docker \
    || echo "⚠️ Space already exists"

echo "📤 Pushing code to HF..."

HF_REPO_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

if git remote | grep hf; then
    echo "✅ Remote already exists"
else
    git remote add hf $HF_REPO_URL
fi

git add .
git commit -m "Deploy Docker Space 🚀" || echo "No changes to commit"

git push hf main

echo "✅ DONE! Docker Space deployed 🚀"
