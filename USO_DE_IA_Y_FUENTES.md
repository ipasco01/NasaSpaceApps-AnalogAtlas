# Analog Atlas · Use of AI, NASA data and references

Team Ctrl Z · NASA Space Apps Piura 2026 · Challenge: *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars*

## 1. Use of AI

The idea and the scope of Analog Atlas are the team's own. We used Claude (Anthropic) as an assistant to research background (earlier analog studies and available datasets), to help write and debug code, and to polish documentation. The team reviewed every AI output before using it: dataset IDs were checked against the official catalogs, planetary files against their PDS labels, and reference values against the papers listed below.

**Inside the product:** the "Ask" box turns a plain-language goal into filter weights. In this version it works with keyword rules, not with an AI model. The similarity scores always come from the engine described in the README.

## 2. NASA data (how each one is used)

| Dataset | Agency | Variables used | How it contributes |
|---|---|---|---|
| MODIS Aqua Land Surface Temperature (MYD11A2, v061) | NASA | Day (13:30) and night (01:30) surface temperature, mean 2018-2023 | Day/night temperature and swing compared with Mars and the Moon; permafrost proxy |
| MODIS Vegetation Indices (MOD13A3, v061) | NASA | NDVI, mean 2018-2023 | "No vegetation" similarity |
| MODIS Land Cover CMG (MCD12C1, v061) | NASA | IGBP classes 0 (water), 15 (permanent snow/ice), 16 (barren), 2022 | Land mask; barren and ice fractions |
| MODIS Snow Cover (MOD10A1, v061) | NASA | NDSI snow cover, mean 2018-2023 | Snow cover |
| MERRA-2 aerosols (M2T1NXAER) | NASA | Dust extinction optical thickness at 550 nm (DUEXTTAU), mean 2022 | Airborne dust similarity |
| MOLA MEGDR (4 px/deg) | NASA (PDS Geosciences) | Mars topography | Slope of Mars reference sites |
| LOLA LDEM_4 (4 px/deg) | NASA (PDS Geosciences) | Moon topography | Slope of Moon reference sites |
| Diviner GCP and PRP (LRO) | NASA (PDS Geosciences) | Bolometric temperature by local hour; south-pole max/mean temperature and ice stability depth | Moon reference temperatures (Marius Hills, Shackleton rim) |
| Mars Trek (Viking MDIM 2.1) and Moon Trek (LRO WAC) | NASA | Imagery | Side-by-side visual comparison at matching scale (120 km) |

**Not included yet:** precipitation from GPM IMERG Monthly V07 (NASA / JAXA) was exported but is not in this version of the Earth table, so dryness does not count in the score.

**Other sources**
- ETOPO1 (NOAA) for Earth elevation and slope.
- GLiM, Global Lithological Map (Hartmann & Moosdorf 2012, CC BY 3.0) for the volcanic and sedimentary rock fractions.
- Sentinel-2 cloudless 2021 by EOX (contains modified Copernicus Sentinel data, CC BY-NC-SA 4.0) for Earth imagery.
- Terrain Tiles (Mapzen, AWS Open Data; built from SRTM, ETOPO1 and other sources) for the 3D relief in the place view.
- MEDA (Perseverance) and REMS (Curiosity) ground temperatures, via Atri et al. 2022.

## 3. References

**Data and catalogs**
- Google Earth Engine Data Catalog: MODIS/061/MYD11A2, MOD13A3, MCD12C1, MOD10A1; NASA/GSFC/MERRA/aer/2; NASA/GPM_L3/IMERG_MONTHLY_V07; NOAA/NGDC/ETOPO1.
- NASA PDS Geosciences Node: MGS MOLA MEGDR (megt90n000cb); LRO LOLA LDEM_4; LRO Diviner derived products (global_cumul_avg_cyl_10n20n_002, dlre_prp_south).
- NASA Mars Trek and Moon Trek WMTS tiles (trek.nasa.gov).
- Hartmann, J., Moosdorf, N. (2012). The new global lithological map database GLiM: a representation of rock properties at the Earth surface. Geochemistry, Geophysics, Geosystems 13, Q12004. Data: PANGAEA, doi:10.1594/PANGAEA.788537.
- EOX Sentinel-2 cloudless 2021 (s2cloudless.eox.at).
- USGS/IAU Gazetteer of Planetary Nomenclature, Shackleton, Feature 5450: center 89.67° S, 129.78° E, diameter 20.92 km.
- NASA Mars Fact Sheet (NSSDC): surface pressure 6.36 mb; surface gravity 3.71 m/s² (0.379 of Earth).

**Science**
- Williams, J.-P., Paige, D. A., Greenhagen, B. T., Sefton-Nash, E. (2017). The global surface temperatures of the Moon as measured by the Diviner Lunar Radiometer Experiment. Icarus 283, 300-325.
- Atri, D. et al. (2022). Diurnal variation of the surface temperature of Mars with the Emirates Mars Mission: a comparison with Curiosity and Perseverance rover measurements. MNRAS Letters. arXiv:2204.12850.
- Munguira, A. et al. (2024). One Martian year of near-surface temperatures at Jezero from MEDA measurements. JGR Planets, doi:10.1029/2024JE008385.
- Hassler, D. M. et al. (2014). Mars' surface radiation environment measured with the Mars Science Laboratory's Curiosity rover. Science 343. Value used: 0.67 mSv/day.
- UNSCEAR (2008). Sources and Effects of Ionizing Radiation, Vol. I, Annex B. Worldwide average natural background dose: 2.4 mSv/year (about 0.007 mSv/day), used in the "What Earth can't reproduce" block.
- Schulze-Makuch, D. et al. (2011). A two-tiered approach to assessing the habitability of exoplanets. Astrobiology 11(10), 1041-1052.
- Peña-Asensio, E. et al. (2024). Evaluating potential landing sites for the Artemis III mission using a multi-criteria decision making approach. arXiv:2406.19863.

**Precedents (how analog sites were chosen before)**
- Haughton-Mars Project, Devon Island; CMU 2009 report on Haughton as a lunar analog.
- NASA Desert RATS at Black Point Lava Flow (NASA Analogs Fact Sheet 2008; D-RATS 2022 report, NTRS 20230007175).
- Río Tinto (Springer Encyclopedia of Astrobiology); Atacama Desert as a Mars analog (Frontiers in Astronomy and Space Sciences, 2021).
- Analog Conjunctive Method, Kuwait (figshare dataset 28599647).
- ESA/Open University Catalogue of Planetary Analogues; Europlanet TA1 Planetary Field Analogues; IMEWG Mars analogue database.

**Software**
- Google Earth Engine; Python (pandas, numpy, rasterio, pyarrow, Pillow); FastAPI and Uvicorn; React 18, Vite and MapLibre GL; Docker.
