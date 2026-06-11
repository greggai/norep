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

## 4b. Aplikacje biznesowe z AI — RAG, dane, backend

Dobrane krytycznie pod budowę aplikacji biznesowych z funkcjami AI (wszystkie Jeffallan/claude-skills
TIER 2, chyba że wskazano inaczej):

| Skill | Po co |
|---|---|
| `rag-architect` | Produkcyjny RAG: chunking, embeddingi, vector DB, hybrid search, reranking, ewaluacja retrievalu |
| `prompt-engineer` | Structured outputs, system prompty, frameworki ewaluacji — jakość warstwy LLM w produkcie |
| `postgres-pro` | PostgreSQL (domyślna baza aplikacji biznesowych i dom dla pgvector): EXPLAIN, JSONB, replikacja |
| `database-optimizer` | Indeksy, plany zapytań, tuning, partycjonowanie (PostgreSQL + MySQL) |
| `fastapi-expert` | Standard backendów AI: async Python, Pydantic v2, JWT, async SQLAlchemy, WebSocket |
| `nextjs-developer` | App Router, Server Components/Actions, route handlers — frontend aplikacji |
| `planning-with-files` (OthmanAdi, 13,4k★, TIER 2) | Trwały stan długich projektów w plikach — #4 rankingu TOP Dev bazy |

Świadomie pominięte (duplikaty): `sql-pro` (pokryte przez postgres-pro + database-optimizer),
`typescript-pro`/`python-pro` (generyczna wiedza językowa bez wartości dodanej ponad model).

## 5. Audyt bezpieczeństwa i weryfikacja kodu

| Element | Źródło | Trust |
|---|---|---|
| `security-reviewer` (audyt z raportem: severity, remediacja, SAST, dependency audit, secrets) | Jeffallan/claude-skills | TIER 2 |
| `secure-code-guardian` (OWASP Top 10, auth, walidacja wejścia, CORS/CSP, JWT) | Jeffallan/claude-skills | TIER 2 |
| `test-master` (testy unit/integration/E2E, security testing OWASP, coverage) | Jeffallan/claude-skills | TIER 2 |
| `github-security-review` (alerty Code Scanning / Dependabot / Secret Scanning → plan remediacji) | MaTriXy/github-review-skill | Community |
| `/security-review` | wbudowane w Claude Code | TIER 1 (Anthropic) |
| claude-code-security-review w CI/CD | docs/claude-security-review.example.yml | TIER 1 (Anthropic) |

Pluginy **Trail of Bits** (TIER 1 — legendarna firma audytorska) w `.claude/settings.json`,
marketplace `trailofbits`:

| Plugin | Po co |
|---|---|
| `audit-context-building` | Budowa głębokiego kontekstu architektury przed polowaniem na podatności |
| `differential-review` | Security review zmian (diff) z analizą historii git |
| `static-analysis` | CodeQL + Semgrep + parsowanie SARIF |
| `semgrep-rule-creator` | Własne reguły Semgrep pod wzorce błędów w Twoim kodzie |
| `insecure-defaults` | Hardcoded credentials, niebezpieczne konfiguracje domyślne |
| `sharp-edges` | API i konstrukcje podatne na błędne użycie (footguns) |
| `variant-analysis` | Szukanie wariantów znalezionej podatności w całym codebase |
| `fp-check` | Systematyczna weryfikacja false positives przed raportowaniem |
| `supply-chain-risk-auditor` | Audyt ryzyka łańcucha dostaw zależności |
| `testing-handbook-skills` | Metodologia z Trail of Bits AppSec Testing Handbook (appsec.guide) |

W marketplace `trailofbits` jest też ~25 dalszych pluginów (m.in. smart contracts,
property-based testing, mutation testing, C/C++ review) — włączysz je przez `/plugin`.

Sugerowany pipeline weryfikacji przed merge:
`audit-context-building` → `/security-review` + `differential-review` → `static-analysis` /
`insecure-defaults` / `sharp-edges` → `fp-check` → `variant-analysis` → `test-master` (testy regresyjne).

## Licencje

Vendorowane skille zachowują pliki LICENSE/LICENSE.txt w swoich katalogach.
Źródła i wersje: commit z dnia 2026-06-11 (klon `--depth 1` z GitHub).
