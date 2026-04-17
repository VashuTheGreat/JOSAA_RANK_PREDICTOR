#!/bin/bash

set -e

PROJECT_NAME="JOSAA_RANK_PREDICTOR"
HF_USERNAME="VashuTheGreat2"   # change this
SPACE_NAME="$PROJECT_NAME"

echo "📁 Using current workspace (Jenkins already cloned repo)"
pwd
ls -la

echo "🤗 Checking Hugging Face CLI..."

if ! command -v huggingface-cli &> /dev/null
then
    echo "❌ HF CLI not found. Installing..."
    pip install -U huggingface_hub
else
    echo "✅ HF CLI already installed"
fi

echo "🔐 Logging into Hugging Face..."

# IMPORTANT: use token instead of interactive login
if [ -z "$HF_TOKEN" ]; then
    echo "❌ HF_TOKEN not set! Add it in Jenkins environment variables"
    exit 1
fi

huggingface-cli login --token $HF_TOKEN

echo "📝 Creating/Updating README.md for Hugging Face Space..."

cat > README.md <<EOF
---
title: $SPACE_NAME
emoji: 🚀
colorFrom: pink
colorTo: purple
sdk: gradio
pinned: false
license: mit
---

# $SPACE_NAME

Auto deployed via Jenkins 🚀
EOF

echo "🚀 Creating Hugging Face Space (if not exists)..."

huggingface-cli repo create $SPACE_NAME \
    --type space \
    --space-sdk gradio \
    || echo "⚠️ Space already exists, continuing..."

echo "📤 Pushing code to Hugging Face Space..."

HF_REPO_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

# Add remote if not exists
if git remote | grep hf; then
    echo "✅ Remote already exists"
else
    git remote add hf $HF_REPO_URL
fi

git add .
git commit -m "Auto deploy to HF Space 🚀" || echo "No changes to commit"

git push hf main

echo "✅ DONE! Your Space is live 🚀"
