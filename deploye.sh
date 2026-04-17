#!/bin/bash
set -e

echo "📁 Using Jenkins workspace..."
cd "$WORKSPACE" || pwd

echo "🔧 Setting git identity..."
git config --global user.name "jenkins"
git config --global user.email "jenkins@local"

echo "🔍 Checking HF CLI..."
export PATH=$HOME/.local/bin:$PATH

if ! command -v hf &> /dev/null; then
    pip3 install --user -U huggingface_hub
fi

echo "🔐 HF Login..."
hf auth login --token "$HF_TOKEN"

HF_USERNAME="VashuTheGreat2"
SPACE_NAME="JOSAA_RANK_PREDICTOR"

echo "🚀 Creating HF Space..."
hf repos create "$HF_USERNAME/$SPACE_NAME" --type space --sdk docker || true

echo "📤 Uploading project (NO git push)..."
hf upload "$SPACE_NAME" . \
  --repo-type=space \
  --repo-id="$HF_USERNAME/$SPACE_NAME"

echo "✅ DEPLOY DONE 🚀"
