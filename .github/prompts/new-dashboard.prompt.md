---
description: "Scaffold a new dashboard app — creates app folder, config, data_loader, sections, registers in hub"
---
Create a new dashboard app called "${input:appName}" in `apps/${input:appName}/`.

Follow the standard pattern from `apps/group_executive_report/` and `apps/operations_monitor/`:
1. Create `config.py` with page settings and column mappings
2. Create `data_loader.py` with CSV source pointing to the sample file
3. Create `app.py` orchestrator with theme, sidebar, data loading, and sections
4. Create `app.yaml` and `requirements.txt`
5. Create `sections/__init__.py` and individual section files
6. Register in `hub/hub_config.py` with the next available port
7. Add to `scripts/run_local.ps1`
8. Update `README.md` and `CHANGELOG.md`
9. Test the app runs locally

The data source is: ${input:dataDescription}
