# Human Docs: Mittelö AI Integrations

This guide details how to set up and use the AI backends integrated into the Mittelö swarm.

## 1. Kimi (Moonshot AI) - "The Coder"

The official Kimi CLI (`kimi-for-coding`) is our primary coding agent.

### Setup
1.  **Install:** `uv tool install kimi-cli`
2.  **Key:** Get key from [platform.moonshot.ai](https://platform.moonshot.ai/console/api-keys).
    - Saved in: `~/.ssh/kimi.token`
3.  **Configure:**
    - Run: `kimi`
    - Input API Key when prompted.
    - Select Model: `kimi-for-coding` (alias `kimi-k2-instruct`).
4.  **Usage in Mittelö:**
    - The backend `backends/kimi/run` uses the configured CLI.

### Resources
- **Docs:** [Kimi Coding Docs](https://www.kimi.com/coding/docs/en/)

## 2. Claude Code + z.ai (GLM-4.6) - "The Architect"

We use the Claude Code CLI but route it through z.ai to access GLM-4.6 models.

### Setup
1.  **Install:** `npm install -g @anthropic-ai/claude-code`
2.  **Key:** Get key from [z.ai](https://z.ai/manage-apikey).
    - Saved in: `~/.ssh/zai.token`
3.  **Configure:** `~/.claude/settings.json` (or `config.json`)

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "YOUR_ZAI_API_KEY",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.6"
  }
}
```

### GLM-4.6V (Vision)
GLM-4.6V has arrived! It supports visual recognition, OCR, and UI replication.
- To use Vision, ensure the prompt includes image references or file paths that the CLI can upload.

## 3. Gemini (Google) - "The Lead"

The Gemini CLI is used for general reasoning and coordination.

## 4. Kiro (Local) - "The Tester"

Local CLI tool (`kiro-cli`) used for rapid testing and chaos simulation.
- **Path:** `/Users/tiny/.local/bin/kiro-cli`

---

## Appendix: About z.ai (Zhipu AI)

**Z.ai** (Beijing Zhipu Huazhang Technology Co., Ltd., est. 2019) is a leading Chinese AI company.

### Key Models
- **GLM-4.6:** Flagship model, SOTA performance.
- **GLM-4.6V:** Multimodal (Vision) model. Supports visual recognition, OCR, UI replication, and video understanding.
- **GLM-4.5-Air:** Lightweight, cost-effective flagship variant.
- **GLM-4.5-Flash:** Free, highly efficient model.
- **GLM-4-32B:** General-purpose large language model (128k context).

### Services
- **API Services:** Integrate models into apps (Anthropic-compatible endpoint).
- **Z.ai Chat:** Free chat platform.
- **Agents:** Translation, Presentation, Video Effects, AI Coding.
- **Generative:** Image, Video, Voice.

### Use Cases
App building, coding assistance, content creation, professional writing, and customer service.