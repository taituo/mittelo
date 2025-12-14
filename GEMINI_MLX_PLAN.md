# GEMINI_MLX_PLAN (Apple Silicon Backend)

Date: 2025-12-14
Owner: Gemini
Goal: Implement a local, hardware-accelerated backend using Apple's MLX.

## Scope
- `backends/mlx/run`: Wrapper script.
- `src/wrapper/drivers/mlx_cli.py`: Driver logic using `mlx_lm.generate`.
- Env Var: `MITTELO_MLX_MODEL` (default: `mlx-community/Qwen2.5-1.5B-Instruct-4bit`).

## Implementation Details

### Driver (`src/wrapper/drivers/mlx_cli.py`)
- **Binary**: `python3 -m mlx_lm.generate` (via subprocess).
- **Arguments**:
  - `--model <model>`
  - `--prompt <prompt>`
  - `--max-tokens 1024` (reasonable default)
  - `--temp 0.7`
- **Output Cleaning**: `mlx_lm` might print loading bars or stats. Need to ensure clean stdout or parse it.

### Backend Script (`backends/mlx/run`)
- Standard python wrapper importing `MlxCLIDriver`.

### Verification
- Install `mlx-lm`: `uv pip install mlx-lm` (if compatible) or rely on user environment.
- Run: `MITTELO_MLX_MODEL=mlx-community/Qwen2.5-1.5B-Instruct-4bit python3 -m mittelo agent --backend mlx --once`

## Deliverables
- [ ] `src/wrapper/drivers/mlx_cli.py`
- [ ] `backends/mlx/run`
- [ ] `docs/BACKENDS.md` update
