# Abdominal obesity measured at health screening across districts of South Korea, 2019-2024

Analysis code for the manuscript

> Kim S. *Abdominal obesity measured at Korean health screening is lower in districts with more university-educated adults.*

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24355789 (v1.0.0).

This code is released under the MIT licence.

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected counts, result tables and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts |
| `04_분석/WAIST/` | Covariate pool and model settings (`make_pool_sets_waist.py`, `sets_WAIST_*.json`, `config_WAIST_main.json`), the full model chain (`run_chain.sh`) and the district adjacency graph (`graph_593.graph`). Sensitivity versions: queen contiguity graph `s577`, without the share aged 80 or older `s2`, unstandardised expected counts `sc`, 2013-2017 `aux`, 2013-2024 including 2018 `full`, second fit of the principal model `rep` |
| `04_분석/WAIST/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material (`numbers_waist.py`, `figs_waist.py`, `content_waist.py`, `build_orcp_waist.py`, `esm_waist.py`, `build_refs_waist.py`) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Attendees with abdominal obesity (waist circumference at least 90 cm in men or 85 cm in women) and attendees by district and sex: National Health Insurance Service screening statistics, KOSIS DT_35007_N138, 2013-2024; national values by sex and age, DT_35007_N139; general screening attendees, DT_35007_N099; first-stage targets and attendees, DT_35007_N001.
- Population by sex and 5-year age group: Ministry of the Interior and Safety, resident registration statistics.
- District covariates: Community Health Survey (walking, high-risk drinking, current smoking, perceived stress, self-reported obesity), local licensing data (general restaurants, instant food businesses), KOSIS local indicators (registered cars, fixed adjustments, negative controls), census (tertiary education), basic livelihood security statistics.

## Pipeline

Set `ST_DATA_ROOT` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database, then run from the repository root.

| Step | Script | Output |
|---|---|---|
| 1 | `99W_build_E_waist.py` (uses `38_build_Estd_all.py`, `40_region_crosswalk.py`, `50_build_master_panel.py`) | District counts (code-based linkage; Sejong from province-level rows) and expected counts by indirect standardisation in 2 sexes x 15 age groups, 2019-2024 (principal), 2013-2017 and 2013-2024 |
| 2 | `99c_extra_canonical_pool_digx.py`, `99c_extra_canonical_pool_lipt.py`, then `04_분석/WAIST/make_pool_sets_waist.py` | Covariate pool and model settings; comparison outcome (metabolic syndrome) |
| 3 | `04_분석/WAIST/run_chain.sh` | Analytic panels (`80_build_disease_panel_v.py`), principal model and multiverse (`81_fit_inla.R`), maps, sensitivity suite (`88g_*`), space-time interaction and spatial confounding models (`88k_*`, `kh_constraints_waist.R`) |
| 4 | `04_분석/WAIST/MS/build/numbers_waist.py`, `figs_waist.py`, `build_orcp_waist.py`, `esm_waist.py` | Manuscript numbers, figures, tables and supplementary material |

R 4.6.0 with R-INLA 25.10.19 (single thread, fixed seeds); Python 3.9 with pandas, geopandas, scipy, matplotlib and python-docx.

## Licence

MIT (see `LICENSE`).
