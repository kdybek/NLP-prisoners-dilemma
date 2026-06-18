#!/usr/bin/env bash
set -e

models=(
  "qwen3.5:9b"
  "ministral-3:8b"
  "ministral-3:14b"
)

prompt_files=(
  "prompts/compassionate.json"
  "prompts/narcissistic.json"
)

for model in "${models[@]}"; do
  for prompt_file in "${prompt_files[@]}"; do
    python play.py \
      --model "$model" \
      --prompt_file "$prompt_file"
  done
done
