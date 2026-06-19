#!/usr/bin/env bash
set -e

models=(
  "qwen3.5:9b"
  "ministral-3:8b"
  "ministral-3:14b"
)

for model in "${models[@]}"; do
  python play.py \
    --model "$model" \
    --prompt_file "prompts/x10.json" \
    --prompt_score_multiplier 10

  python play.py \
    --model "$model" \
    --prompt_file "prompts/x100.json" \
    --prompt_score_multiplier 100
done

