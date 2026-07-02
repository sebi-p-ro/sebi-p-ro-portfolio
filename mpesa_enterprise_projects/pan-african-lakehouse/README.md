# 🏠 Pan-African Medallion Lakehouse

This folder now serves as a minimal medallion-style example. It demonstrates how a small dbt project can be structured around bronze, silver, and gold layers without assuming a live warehouse is available.

## What is included
- A lightweight dbt project with a simple profile definition.
- A bronze model that demonstrates raw input shaping.
- A silver model that references the bronze model.

## How to run locally
```bash
cd mpesa_enterprise_projects/pan-african-lakehouse/dbt
dbt parse --profiles-dir .
```

## Notes
This is intentionally a starter example, not a full production lakehouse implementation.
