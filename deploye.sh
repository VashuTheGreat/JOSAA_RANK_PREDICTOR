#!/bin/bash

set -e

REPO_URL="https://github.com/VashuTheGreat/JOSAA_RANK_PREDICTOR.git"
PROJECT_NAME="JOSAA_RANK_PREDICTOR"
HF_USERNAME="VashuTheGreat2"   # <-- change this
SPACE_NAME="$PROJECT_NAME"

echo "🔍 Checking Git..."

if ! command -v git &> /dev/null
then
    echo "❌ Git not found. Installing..."
    sudo apt update
    sudo apt install -y git
else
    echo "✅ Git already installed"
fi

echo "📥 Cloning repo..."
if [ -d "$PROJECT_NAME" ]; then
    echo "⚠️ Directory exists, pulling latest code..."
    cd $PROJECT_NAME
    git pull
else
    git clone $REPO_URL
    cd $PROJECT_NAME
fi

echo "🔍 Checking Docker..."

if ! command -v docker &> /dev/null
then
    echo "❌ Docker not found. Installing..."
    sudo apt update
    sudo apt install -y docker.io

    echo "🔧 Adding user to docker group..."
    sudo usermod -aG docker $USER
    newgrp docker
else
    echo "✅ Docker already installed"
fi

echo "🐳 Building Docker image..."
docker build -t josaa_predictor .

echo "🤗 Checking Hugging Face CLI..."

if ! command -v huggingface-cli &> /dev/null
then
    echo "❌ HF CLI not found. Installing..."
    pip install -U huggingface_hub
else
    echo "✅ HF CLI already installed"
fi

echo "🔐 Login to Hugging Face"
huggingface-cli login

echo "📝 Creating/Overriding README.md for Hugging Face Space..."

cat > README.md <<EOF
---
title: $SPACE_NAME
emoji: 🦀
colorFrom: pink
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# $SPACE_NAME

This space is automatically deployed using a shell script 🚀
EOF

echo "🚀 Creating or updating Hugging Face Space..."

huggingface-cli repo create $SPACE_NAME \
    --type space \
    --space-sdk docker \
    || echo "⚠️ Space may already exist, continuing..."

echo "📤 Pushing code to Hugging Face Space..."

HF_REPO_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

if git remote | grep hf; then
    echo "Remote already exists"
else
    git remote add hf $HF_REPO_URL
fi

git add .
git commit -m "Auto deploy with updated README" || true
git push hf main

echo "✅ DONE! Your Space is live 🚀"
