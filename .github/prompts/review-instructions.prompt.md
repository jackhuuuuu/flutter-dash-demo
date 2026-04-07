---
description: "Review and update the copilot-instructions.md file to reflect the current state of the project"
---
Review `.github/copilot-instructions.md` against the actual project state.

Check and fix:
1. **Current Dashboards table** — scan `hub/hub_config.py` for all registered apps and ensure the table matches
2. **Reusable Components list** — scan `flutter_dash/components/__init__.py` for all exports and update the list
3. **Common Pitfalls** — remove any that no longer apply, keep those that do
4. **Project Context** — add any new context from recent conversations
5. **Key Conventions** — verify against actual code patterns in `apps/` and `flutter_dash/`

Show me a summary of what changed.
