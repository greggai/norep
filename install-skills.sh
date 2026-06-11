#!/usr/bin/env bash
# Instalacja pakietu Claude Skills — elementy, których nie da się zwendorować w repo.
# Skille w .claude/skills/, pluginy w .claude/settings.json i MCP w .mcp.json
# ładują się automatycznie po otwarciu tego repo w Claude Code (zaakceptuj prompt zaufania).
#
# Ten skrypt uruchom RAZ, lokalnie, wewnątrz Claude Code lub w terminalu obok niego.
set -euo pipefail

echo "== 1. GSD (open-gsd/gsd-core) — framework PM, TIER 1 =="
echo "   Instaluje komendy /gsd-* w bieżącym projekcie:"
npx --yes @opengsd/gsd-core@latest || echo "   (pomiń, jeśli nie chcesz GSD w tym projekcie)"

echo ""
echo "== 2. dev-browser — runtime (plugin włączony w .claude/settings.json) =="
echo "   Plugin wymaga Node 18+; daemon zainstaluje się przy pierwszym użyciu skilla."

echo ""
echo "== 3. Fine-tuning =="
echo "   hf-skills (Hugging Face, TIER 1) jest już w .mcp.json — wymaga konta HF przy treningu."
echo "   Opcjonalne community skille (zweryfikuj przed użyciem — trust: Community):"
echo "   - Local LLM Fine-Tuning oraz LLM Fine-Tuning (Unsloth): sync z MCP Market (mcpmarket.com)"

echo ""
echo "== 4. Automatyzacje — elementy poza repo =="
echo "   - Anthropic Channels: wbudowane w Claude Code (Pro/Max/Team) — nic nie instalujesz."
echo "   - n8n: self-host lub cloud + node 'AI Agent' z Claude API (https://n8n.io)."
echo "   - Zapier: subskrypcja + Claude API (szybszy setup, mniejsza elastyczność niż n8n)."
echo "   - claude-code-security-review (GitHub Action): patrz docs/claude-security-review.example.yml;"
echo "     wymaga sekretu ANTHROPIC_API_KEY w repo. Komenda /security-review działa już teraz."

echo ""
echo "Gotowe. Szczegóły pakietu: SKILLS.md"
