# BATAYAN benchmark of Bintanong's Gemma 4 E4B (handover, 8 November 2026)

BATAYAN (Montalan et al., 2025) is the Filipino task group in AI Singapore's SEA-HELM. It measures the
**language model** that Bintanong uses (Gemma 4 E4B, Q4_K_XL GGUF, Bintanong's inference settings). It does not
measure the RAG pipeline; that is RAGAS (`../ragas/`). `--tasks batayan` covers 9 Tagalog tasks with 3,800 items
in total, matching Montalan Table 2: sentiment, belebele-qa-mc, toxicity, paraphrase, translation-en-xx,
translation-xx-en, abssum, causal and nli. All tasks are zero-shot with Filipino prompts and one run.

## Status

| Part | State |
| --- | --- |
| Pilot (5 items per task, `--limit 5`) | Done on 8 Nov. 0 failures, every answer `finish_reason=stop`, no thinking output. `results/pilot-5-per-task-results-2026-11-08.json`. Pilot scores are only a smoke test, not results. |
| Sentiment (600 items) | Done on 8 Nov. Macro F1 **73.48**, accuracy 75.5, 0 unparseable answers. `results/sentiment-only-results-2026-11-08.json` |
| The other 8 tasks | **Not run.** At 02:14 on 8 Nov the 4 GB-GPU / 16 GB-RAM laptop ran out of RAM; Windows killed the model server during Belebele. Run them on a machine with more memory, using the steps below. |

## What the next developer needs

You need: Git, Python **3.12** (not 3.13: `pyonmttok` has no 3.13 wheel), Docker with an NVIDIA GPU, and your
own Gemma 4 E4B GGUF (`gemma-4-E4B-it-UD-Q4_K_XL.gguf`), plus a free Hugging Face account. Nothing here downloads
or stores model weights.

### 1. Get Hugging Face access (once)
1. Sign in at huggingface.co and open each dataset page below. Click "Agree and access" (approval is automatic):
   `aisingapore/NLU-Sentiment-Analysis`, `NLU-Belebele-MCQA`, `Safety-Toxicity-Detection`, `NLR-Causal-Reasoning`,
   `NLR-NLI`, `NLG-Machine-Translation`, `NLG-Abstractive-Summarization`.
2. Create a **Read** token (Settings > Access Tokens). Keep it out of Git and chat.

### 2. Make a work folder outside the repository
Use any folder, for example `bintanong_workspace/audit-evidence/batayan-<date>/`, which is ignored by Git.
Run these commands from inside it (Git Bash on Windows, or any shell on Linux):

```bash
git clone https://github.com/aisingapore/sea-helm.git
git -C sea-helm checkout 9be3986d00185dc6d6ec362b71542ed29642a6be
git -C sea-helm apply <repo>/docs/evaluation/batayan/scripts/sea-helm-local-changes.patch
py -3.12 -m venv .venv            # Linux: python3.12 -m venv .venv
.venv/Scripts/python -m pip install -r <repo>/docs/evaluation/batayan/scripts/requirements-frozen.txt
                                  # Linux: .venv/bin/python -m pip install ...
echo "HF_TOKEN=<your read token>" > .env
```

`git apply` must print nothing. If it fails, you are not on commit `9be3986`.

### 3. Start the model server (same image and flags as our run)
Point the bind mount at the folder that holds your GGUF:

```bash
docker run -d --name batayan-gemma --gpus all -p 127.0.0.1:18088:8080 \
  -v "<your models folder>:/models:ro" \
  ghcr.io/ggml-org/llama.cpp@sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d \
  --model /models/<path>/gemma-4-E4B-it-UD-Q4_K_XL.gguf --host 0.0.0.0 --port 8080 \
  --ctx-size 8192 --parallel 1 --threads 8 --n-predict 768 --n-gpu-layers auto --fit-target 512 \
  --log-verbosity 4 --no-webui --jinja
curl http://127.0.0.1:18088/health   # wait for {"status":"ok"}
```

Keep `--jinja`, `--parallel 1` and `--n-predict 768` so scores stay comparable with our Sentiment result.
If you already serve the model on another port, set `MODEL_URL=http://127.0.0.1:<port>/v1` instead.

### 4. Pilot, then the full run

```bash
bash <repo>/docs/evaluation/batayan/scripts/run_batayan.sh . ../pilot --limit 5 > pilot.log 2>&1   # about 4 minutes
bash <repo>/docs/evaluation/batayan/scripts/run_batayan.sh . ../full-run > full-run.log 2>&1
```

Check the pilot first: `grep -c "Failed to run" pilot.log` must give 0. Then open a few
`*_batch_response.jsonl` files under `pilot/.../inferences/tl/`. Answers must have `"finish_reason": "stop"` and
contain no thinking text. The full run took about 5.5 minutes for Sentiment on an RTX 3050 laptop. On that
machine all 9 tasks were estimated at 3.5-4.5 hours, so expect less on a faster GPU. If the run stops, rerun
the same command with the same output folder: SEA-HELM reuses finished tasks' saved answers
(`--rerun_cached_results` would redo them).

### 5. Check and hand back
- `grep -c "Failed to run" full-run.log` must be **0**. Fix and rerun any failed task before reporting.
- The scores are in `full-run/gemma-4-E4B-it-UD-Q4_K_XL/run_0/results/*_seahelm_results_*.json` and at the end
  of the log (`Overall normalized score for <tl_nlu>`, `<tl_nlr>`, `<tl_nlg>`, `<tl_safety>`).
- Your Sentiment Macro F1 should be close to **73.48**. A large difference means a different model file,
  server flags or patch.
- Copy the results JSON (not the `.env`, not inference dumps) into `docs/evaluation/batayan/results/`,
  stage it explicitly, and commit on `p12-batayan-benchmark`. No AI attribution lines in commit messages.

## Differences from the published SEA-HELM set-up (report these with the scores)

`scripts/sea-helm-local-changes.patch` holds every change:
- **Translation:** MetricX-24 (a 13B judge model that needs a large GPU) and its judges are turned off. ChrF++ is
  the translation metric instead. Translation scores are therefore not comparable with leaderboard MT scores.
- **Summarization:** ChrF++ is added next to ROUGE-L; ROUGE-L stays the headline metric. BERTScore is not used.
- **Inference settings:** the same as Bintanong's runtime: temperature 0, `reasoning_effort: none`, prompt cache
  on, and token 100 (`<|channel>`, Gemma 4's thinking opener) banned. Without this, Gemma spent its output
  budget thinking and returned empty answers.
- **Windows fixes:** log names without colons, and a fresh HTTP client per event loop. These do not affect
  scores and are harmless on Linux.
- The model is a 4-bit quantized GGUF served by llama.cpp, not the full-precision weights the leaderboard uses.

For context, the SEA-HELM Tagalog leaderboard (18 Sep 2026) lists Gemma 4 E2B at NLU 69.72 / NLR 59.36 /
NLG 54.07 and Gemma 4 31B at 76.85 / 82.85 / 58.92. E4B is not listed. Compare only NLU and NLR directly; NLG
differs because of the metric change above.

## Files

| File | Purpose |
| --- | --- |
| `scripts/run_batayan.sh` | Runs `--tasks batayan` against the model server |
| `scripts/sea-helm-local-changes.patch` | Every local change to SEA-HELM `9be3986` |
| `scripts/requirements-frozen.txt` | Exact Python 3.12 packages of our venv |
| `results/sentiment-only-results-2026-11-08.json` | Scored Sentiment; the other tasks show the crash error |
| `results/pilot-5-per-task-results-2026-11-08.json` | 5-item smoke test of all tasks |
