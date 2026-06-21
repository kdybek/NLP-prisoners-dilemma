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
    --prompt_file "prompts/independent_payoffs_coop.json" \
    --independent_payoffs "coop"

  python play.py \
    --model "$model" \
    --prompt_file "prompts/independent_payoffs_defect.json" \
    --independent_payoffs "defect"
done

