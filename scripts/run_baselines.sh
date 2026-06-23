#!/usr/bin/env bash
set -e

models=(
  "qwen3.5:9b"
  "ministral-3:8b"
  "ministral-3:14b"
  "random"
)

for model in "${models[@]}"; do
  python play.py \
    --model "$model" \
    --prompt_file "prompts/baseline.json"
done

