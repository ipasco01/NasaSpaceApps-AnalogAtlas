# Analog Atlas · Use of AI, NASA data and references

> Documento para la entrega (en inglés, como piden las bases). Equipo Ctrl Z · NASA Space Apps Piura 2026.
> Regla del equipo: todo dato con su fuente; lo que no está verificado se marca **[to verify]**.
> Completar las filas marcadas **[team: complete]**.

## 1. Use of AI

### 1.1 AI used to build the project

| Tool | Provider | What we used it for | What humans did |
|---|---|---|---|
| Claude (Claude Code, model Claude Opus 5.5) | Anthropic | Architecture and scope planning; research of precedents and datasets (web search, NASA PDS and Earth Engine catalog checks); writing and debugging the data pipeline (Earth Engine script, Python converters, Diviner byte-range reader); the similarity engine; the clickable UI prototype; documentation | Chose the challenge, product and audience; ran every Earth Engine export; reviewed and approved each design and data decision; tested results |
| **[team: complete]** | | Tool used for the "HADES-T" concept text (stress-vector framing, dead-band tolerance) | Adopted only the parts that passed review |
| **[team: complete]** | | Tool used to make the original visual mockup and logo, if any | |

AI output was checked before use: every dataset ID and band was verified in the official Earth Engine catalog (earthengine-stac), every planetary file against its PDS label, and reference values against the papers listed below. Where AI-suggested code failed (Earth Engine "Unable to transform edge"), the team diagnosed and fixed it with test exports.

### 1.2 AI inside the product

- **Ask AI** turns a plain-language goal ("rocky terrain to test rover mobility") into filter weights. Planned model: Claude (Anthropic API) with structured outputs. **In the current prototype the replies are simulated from keywords**; the scores always come from the similarity engine, never from the AI.

## 2. NASA data (how each one is used)

| Dataset | Agency | Variables used | How it contributes |
|---|---|---|---|
| MODIS Aqua Land Surface Temperature (MYD11A2, v061) | NASA | Day (13:30) and night (01:30) surface temperature, 2018-2023 | Day/night temperature and swing compared with Mars and the Moon; permafrost proxy |
| MODIS Vegetation Indices (MOD13A3, v061) | NASA | NDVI, 2018-2023 | "No vegetation" similarity |
| MODIS Land Cover CMG (MCD12C1, v061) | NASA | IGBP classes 0 (water), 15 (permanent snow/ice), 16 (barren), 2022 | Land mask; barren and ice fractions |
| MODIS Snow Cover (MOD10A1, v061) | NASA | NDSI snow cover, 2018-2023 | Snow cover |
| GPM IMERG Monthly (V07) | NASA / JAXA | Precipitation, median 2018-2023 | Dryness (pending final download) |
| MERRA-2 aerosols (M2T1NXAER) | NASA | Dust extinction optical thickness (DUEXTTAU), 2022 | Airborne dust (export in progress) |
| MOLA MEGDR (4 px/deg) | NASA (PDS Geosciences) | Mars topography | Slope of Mars reference sites |
| LOLA LDEM_4 (4 px/deg) | NASA (PDS Geosciences) | Moon topography | Slope of Moon reference sites |
| Diviner GCP and PRP (LRO) | NASA (PDS Geosciences) | Bolometric temperature by local hour; south-pole max/mean temperature and ice stability depth | Moon reference temperatures (Marius Hills, Shackleton rim) |
| Mars Trek (Viking MDIM 2.1) and Moon Trek (LRO WAC) | NASA | Imagery | Side-by-side visual comparison at matching scale (120 km) |

Other sources: ETOPO1 (NOAA) for Earth relief; Sentinel-2 cloudless 2021 by EOX (contains modified Copernicus Sentinel data, CC BY-NC-SA 4.0) for Earth imagery; MEDA (Perseverance) and REMS (Curiosity) ground temperatures via Atri et al. 2022.

## 3. References

**Data and catalogs**
- Google Earth Engine Data Catalog (earthengine-stac): MODIS/061/MYD11A2, MOD13A3, MCD12C1, MOD10A1; NASA/GPM_L3/IMERG_MONTHLY_V07; NASA/GSFC/MERRA/aer/2; NOAA/NGDC/ETOPO1.
- NASA PDS Geosciences Node: MGS MOLA MEGDR (megt90n000cb); LRO LOLA LDEM_4; LRO Diviner derived products (global_cumul_avg_cyl_10n20n_002, dlre_prp_south).
- NASA Mars Trek and Moon Trek WMTS tiles (trek.nasa.gov).
- EOX Sentinel-2 cloudless 2021 (s2cloudless.eox.at).
- USGS/IAU Gazetteer of Planetary Nomenclature, Shackleton, Feature 5450: center 89.67° S, 129.78° E, diameter 20.92 km.
- NASA Mars Fact Sheet (NSSDC, updated 19 May 2025): surface pressure 6.36 mb; surface gravity 3.71 m/s² (0.379 of Earth).

**Science**
- Williams, J.-P., Paige, D. A., Greenhagen, B. T., Sefton-Nash, E. (2017). The global surface temperatures of the Moon as measured by the Diviner Lunar Radiometer Experiment. Icarus 283, 300-325.
- Atri, D. et al. (2022). Diurnal variation of the surface temperature of Mars with the Emirates Mars Mission: a comparison with Curiosity and Perseverance rover measurements. MNRAS Letters. arXiv:2204.12850.
- Hassler, D. M. et al. (2014). Mars' surface radiation environment measured with the Mars Science Laboratory's Curiosity rover. Science 343. Value used: 0.67 mSv/day (SwRI release quoting the RAD team).
- Schulze-Makuch, D. et al. (2011). A two-tiered approach to assessing the habitability of exoplanets (Earth Similarity Index). Astrobiology 11. **[to verify citation details]**
- Peña-Asensio, E. et al. (2024). Evaluating potential landing sites for the Artemis III mission using a multi-criteria decision making approach. arXiv:2406.19863.
- Munguira, A. et al. (2024). One Martian year of near-surface temperatures at Jezero from MEDA measurements. JGR Planets, doi:10.1029/2024JE008385.

**Precedents (how analog sites were chosen before)**
- Haughton-Mars Project, Devon Island (Space.com interview with P. Lee); CMU 2009 report on Haughton as a lunar analog.
- NASA Desert RATS at Black Point Lava Flow (NASA Analogs Fact Sheet 2008; D-RATS 2022 report, NTRS 20230007175).
- Río Tinto (Springer Encyclopedia of Astrobiology); Atacama Desert as a Mars analog (Frontiers in Astronomy and Space Sciences, 2021).
- Analog Conjunctive Method, Kuwait (figshare dataset 28599647).
- ESA/Open University Catalogue of Planetary Analogues; Europlanet TA1 Planetary Field Analogues; IMEWG Mars analogue database.

**Software**
- Google Earth Engine; Python (pandas, numpy, rasterio, pyarrow, Pillow); Streamlit.

## 4. Earth reference value still to verify

- Earth natural background radiation ~2.4 mSv/year (~0.007 mSv/day) used in the "What Earth can't reproduce" block. **[to verify: UNSCEAR source]**
