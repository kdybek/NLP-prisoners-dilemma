#!/usr/bin/env bash
set -e

models=(
  "qwen3.5:9b"
  "ministral-3:8b"
  "ministral-3:14b"
)

prompt_files=(
  "prompts/x10.json"
  "prompts/x100.json"
)

for model in "${models[@]}"; do
  for prompt_file in "${prompt_files[@]}"; do
    if [[ "$prompt_file" == *"x10.json" ]]; then
      multiplier=10
    elif [[ "$prompt_file" == *"x100.json" ]]; then
      multiplier=100
    else
      echo "Unknown prompt file: $prompt_file"
      exit 1
    fi

    python play.py \
      --model "$model" \
      --prompt_file "$prompt_file" \
      --prompt_score_multiplier "$multiplier"
  done
done

