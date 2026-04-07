# Copilot Instructions — FBI Hub Platform

> **SELF-MAINTAINING DOCUMENT** — This file is the single source of truth for
> how Copilot works in this project. It must stay accurate and current.
> See the "Self-Maintenance Rules" section for how and when to update this file.

---

## Project Overview

This is the **FBI Hub** — a multi-app Streamlit dashboard platform for Flutter UK&I.
It consists of a Hub landing page, individual dashboard apps, and a shared component
library called `flutter_dash`.

### Project Context

- The platform serves **Flutter UK&I** (Flutter Entertainment's UK & Ireland division)
- Users are a mix of data engineers, finance analysts, and non-technical stakeholders
- Data flows from **Databricks Unity Catalog** (production) but dashboards are
  developed locally against CSV sample files first
- The DQ monitor view (`global_vw_dq_monitor`) tracks data quality checks
  across brands (currently SBT, more brands coming)
- Future plans include adding **Databricks job/pipeline performance** monitoring
  to the Operations Monitor dashboard
- Each app is independently deployable — if one breaks, others keep running

## Architecture

- **Hub** (`hub/`) — tile-based launcher, app registry in `hub_config.py`
- **Dashboard apps** (`apps/<name>/`) — each is a standalone Streamlit app
- **Shared library** (`flutter_dash/`) — pip-installable package providing themed
  components, charts, data loaders, and formatters

### Current Dashboards

| App | Port | Status |
|-----|------|--------|
| FBI Hub | 8501 | Live |
| Group Executive Report | 8502 | Live |
| Operations Monitor | 8505 | Live |

---

## Key Conventions

### Code Style
- Code is read by **non-technical users** (data engineers, finance analysts).
  Write clear comments, use descriptive variable names, and keep logic simple.
- Every Python file starts with a module docstring explaining what it does.
- Use type hints on function signatures.

### Dashboard App Structure
Each dashboard app follows this pattern:
```
apps/<name>/
├── app.py              # Main orchestrator (theme → sidebar → data → sections)
├── config.py           # All dashboard-specific settings and column mappings
├── data_loader.py      # CSV for local dev, Databricks for production
├── app.yaml            # Databricks Apps deployment config
├── requirements.txt    # Dependencies for deployment
└── sections/           # One file per visual section of the dashboard
    ├── __init__.py
    ├── header.py
    ├── kpi_section.py
    └── ...
```

### Theme System
- All visuals use `ThemeTokens` from `flutter_dash/theme/tokens.py`
- Two palettes: `FLUTTER_DARK` and `FLUTTER_LIGHT` in `palettes.py`
- Theme is toggled via sidebar and passed between apps via URL query param
- All charts, cards, tables, and CSS adapt automatically to the active theme
- When creating new components, always accept an optional `tokens` parameter
  and default to `get_active_theme()`

### Reusable Components (`flutter_dash/components/`)
- `kpi_card` — metric cards with variance comparisons
- `charts.py` — `line_chart`, `bar_chart`, `pie_chart`, `waterfall_chart`, `heatmap_chart`
- `data_table` — hierarchical financial table
- `section_title` — styled section headers
- `sidebar.py` — `SidebarBuilder` for composable sidebars
- When adding new chart types, add them to `charts.py` and export from `__init__.py`
- All Plotly charts must use `base_layout(tokens)` from `flutter_dash/theme/plotly.py`

### Data Loading
- `flutter_dash/data/loader.py` provides `CsvLoader` and `DatabricksLoader`
- Use `get_loader(source, **kwargs)` factory in each app's `data_loader.py`
- Always wrap with `@st.cache_data` for performance

### Streamlit-Specific
- Use `st.markdown(..., unsafe_allow_html=True)` for custom HTML components
- Sidebar selections are extracted as a dict from `SidebarBuilder.render()`

---

## Common Pitfalls (learned from experience)

These are real issues that have come up — follow these rules to avoid them:

- **Stacked bar charts**: when `barmode="stack"`, set `textposition="inside"` with
  `textfont=dict(color="white")`. The default `textposition="outside"` overlaps,
  and the default text colour matches the bar colour (invisible inside).
- **Plotly duplicate IDs**: Streamlit requires every `st.plotly_chart()` to have a
  unique `key=` parameter. This is especially easy to miss when two similar charts
  are rendered in columns (e.g. revenue vs EPM side-by-side).
- **CSV null strings**: Databricks CSV exports write literal `"null"` for missing
  values. Always add `df.replace("null", pd.NA)` in `data_loader.py`.
- **HTML components**: `stc.html()` iframes inherit no styling from Streamlit.
  Always set `background:transparent` on the `<body>` and use `tokens.bg_surface`
  for the card background.
- **Resolution minutes**: always convert to hours for display (÷ 60). Raw minutes
  are not intuitive for non-technical users.

---

## After Every Task

Complete **all** of the following before considering any task done.

### Testing
1. Run the app locally (`streamlit run app.py --server.port <port>`)
2. Verify the health endpoint returns OK (`/_stcore/health`)
3. Check both light and dark themes render correctly
4. Confirm no duplicate element ID errors in the terminal

### Files to Update
- `README.md` — architecture diagram, repo structure, quick start
- `CHANGELOG.md` — document what was added/changed/fixed
- `hub/hub_config.py` — if adding/modifying dashboard apps
- `scripts/run_local.ps1` — if adding new apps
- `flutter_dash/components/__init__.py` — if adding new component exports

Update README and CHANGELOG automatically without being asked.

### Adding a New Dashboard
When adding a new dashboard, also:
1. Create the app folder under `apps/`
2. Add an entry to `hub/hub_config.py` APPS list
3. Add to `scripts/run_local.ps1` apps array

---

## Self-Maintenance Rules

**This file must evolve with the project.** Copilot should review and update
this file as part of its normal workflow — not as a separate task the user
has to remember.

### When to update this file

After completing any task, review this file and apply updates if any of the
following are true:

1. **New dashboard added** → update the "Current Dashboards" table
2. **New component or chart type added** → update the "Reusable Components" list
3. **Bug was caused by a pattern** → add to "Common Pitfalls" section
4. **User mentioned context/background** that would be useful in future
   conversations → capture it in the relevant section
5. **A convention was established** during the conversation (naming pattern,
   file structure, data handling approach) → add to "Key Conventions"
6. **A rule in this file is no longer accurate** (e.g. a component was renamed
   or removed) → update or remove it

### How to update

- Keep entries **short and specific** — one bullet point per rule
- Pitfalls should include: what went wrong, and the correct approach
- Remove rules that no longer apply (don't let this file grow stale)
- Don't duplicate — if something is already covered, don't add it again

### What NOT to put here

- Implementation details that belong in code comments
- Temporary task-specific notes (use session memory for those)
- Full tutorials — link to README instead
