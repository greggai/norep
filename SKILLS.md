# Pakiet Claude Skills — programowanie, UI, API, fine-tuning, automatyzacje

Pakiet zbudowany na bazie `Claude_Skills_Baza_v5_20260610.xlsx` (arkusze: FILTR Claude Code,
TOP Dev i PM, Nowe domeny v5). Wszystko ładuje się automatycznie po otwarciu repo
w Claude Code — przy pierwszym otwarciu zaakceptuj prompt zaufania dla pluginów i MCP.

## Jak to działa

| Mechanizm | Plik | Co zawiera |
|---|---|---|
| Skille projektu (vendored) | `.claude/skills/` | 21 skilli skopiowanych ze źródłowych repo |
| Pluginy marketplace | `.claude/settings.json` | superpowers, dev-browser, 5 pluginów design |
| Serwer MCP | `.mcp.json` | hf-skills (fine-tuning Hugging Face) |
| Reszta (built-in / platformy) | `install-skills.sh` | GSD, Channels, n8n, security-review |

## 0. Fundament

| Skill | Źródło | Trust |
|---|---|---|
| `karpathy-guidelines` | forrestchang/andrej-karpathy-skills | TIER 1 |
| `skill-creator` | anthropics/skills | TIER 1 (Anthropic) |
| `mcp-builder` | anthropics/skills | TIER 1 (Anthropic) |
| plugin `superpowers` (TDD, /brainstorm, /write-plan, /execute-plan) | obra/superpowers-marketplace | TIER 1-2 |
| GSD — `npx @opengsd/gsd-core@latest` (w install-skills.sh) | open-gsd/gsd-core | TIER 1 |

## 1. Aplikacje + nowoczesny wygląd

| Skill | Źródło | Trust |
|---|---|---|
| `frontend-design` | anthropics/skills | TIER 1 |
| `ui-ux-pro-max` (50+ stylów, 161 palet) | nextlevelbuilder/ui-ux-pro-max-skill | Verified |
| `react-best-practices`, `web-design-guidelines`, `composition-patterns`, `react-view-transitions`, `vercel-optimize` | vercel-labs/agent-skills | TIER 1 (Vercel) |
| `accessibility`, `performance`, `core-web-vitals`, `seo`, `best-practices`, `web-quality-audit` | addyosmani/web-quality-skills | TIER 1-2 |
| `3d-frontend` (scroll-driven 3D, Three.js + GSAP) | zyliu0/3d-frontend | Verified |
| pluginy `threejs-webgl`, `gsap-scrolltrigger`, `react-three-fiber`, `motion-framer`, `modern-web-design` (+17 dalszych w marketplace) | freshtechbro/claudedesignskills | Verified |
| `playwright-skill` (testy E2E) | lackeyjb/playwright-skill | TIER 2 |

## 2. Budowanie API

| Skill | Źródło | Trust |
|---|---|---|
| `api-designer` (OpenAPI, modelowanie zasobów, mock, SDK) | Jeffallan/claude-skills | TIER 2 |
| `api-documentation` | sethdford/claude-plugins | Community |
| `mcp-builder` (serwery MCP) | anthropics/skills | TIER 1 |

## 3. Fine-tuning

| Element | Źródło | Trust |
|---|---|---|
| MCP `hf-skills` (SFT/DPO/GRPO, 0.5B-70B, LoRA, GGUF) | huggingface.co/mcp?bouquet=skills | TIER 1 (HF) |
| `fine-tuning-expert` (LoRA/QLoRA, PEFT, datasety JSONL, RLHF/DPO) | Jeffallan/claude-skills | TIER 2 |
| Local LLM Fine-Tuning, Unsloth (opcjonalne) | MCP Market | Community — zweryfikuj przed użyciem |

## 4. Automatyzacje

| Element | Jak | Trust |
|---|---|---|
| Anthropic Channels | wbudowane w Claude Code (Pro/Max/Team) | TIER 1 |
| plugin `dev-browser` (bezpieczna automatyzacja przeglądarki) | .claude/settings.json | Verified |
| `playwright-skill` | .claude/skills/ | TIER 2 |
| claude-code-security-review (CI/CD) | docs/claude-security-review.example.yml + sekret ANTHROPIC_API_KEY; lokalnie: /security-review | TIER 1 |
| n8n + Claude / Zapier + Claude | platformy zewnętrzne — patrz install-skills.sh | TIER 1 / Verified |

## Licencje

Vendorowane skille zachowują pliki LICENSE/LICENSE.txt w swoich katalogach.
Źródła i wersje: commit z dnia 2026-06-11 (klon `--depth 1` z GitHub).
