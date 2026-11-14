// Atlas Analog · earth_engine_tierra.js
// v0.9 · 2026-11-14 · Isabelita (equipo Ctrl Z)
// Exportación de la Tierra desde code.earthengine.google.com. Registro de lo que funcionó y lo que no:
//
// FUNCIONÓ (v6, región -180..180 + crs + crsTransform, máscara MCD12C1):
//   temperatura: MODIS/061/MYD11A2 (sinusoidal 1 km)  -> temp_dia, temp_noche, rango_termico, permafrost_proxy
//   nieve:       MODIS/061/MOD10A1 (sinusoidal 500 m) -> nieve
//   relieve:     NOAA/NGDC/ETOPO1 (1 arcmin)           -> elevacion (pendiente en tif_a_tabla.py)
// FALLÓ en segundos con "Unable to transform edge (256,256 ...)": MODIS/061/MOD13C1 y NASA/GPM_L3/IMERG_MONTHLY_V07
// v8 polvo (NASA/GSFC/MERRA/aer/2) no falló al inicio; resultado pendiente.
// v9 (este archivo): reemplazos de lo que falló. Datasets y bandas verificados en earthengine-stac el 2026-11-14.

var INICIO = '2018-01-01';
var FIN    = '2023-12-31';
var MUNDO  = ee.Geometry.Rectangle([-180, -90, 180, 90], null, false);
var GRILLA = [0.25, 0, -180, 0, -0.25, 90];

var cobertura = ee.ImageCollection('MODIS/061/MCD12C1')
  .filterDate('2022-01-01', '2023-01-01').first().select('Majority_Land_Cover_Type_1');
var tierraFirme = cobertura.neq(0);   // 0 = agua en MCD12C1

var sinusoidal = ee.ImageCollection('MODIS/061/MYD11A2').first().projection().atScale(5000);

var vegetacion = ee.Image.cat([
    ee.ImageCollection('MODIS/061/MOD13A3').filterDate(INICIO, FIN)
      .select('NDVI').mean().multiply(0.0001).rename('ndvi'),   // escala 0,0001 (catálogo)
    cobertura.eq(16).rename('arido'), cobertura.eq(15).rename('hielo')
  ]).toFloat().updateMask(tierraFirme);

var lluviaGpm = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07').filterDate(INICIO, FIN)
  .select('precipitation').median().multiply(24 * 365).rename('lluvia')   // mm/h -> mm/año
  .reproject(sinusoidal).toFloat().updateMask(tierraFirme);

var lluviaEra5 = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate(INICIO, FIN)
  .select('total_precipitation_sum').median().multiply(12 * 1000).rename('lluvia')   // m/mes -> mm/año
  .toFloat().updateMask(tierraFirme);

var polvo = ee.ImageCollection('NASA/GSFC/MERRA/aer/2').filterDate('2022-01-01', '2023-01-01')
  .select('DUEXTTAU').mean().rename('polvo').toFloat().updateMask(tierraFirme);

var tareas = {vegetacion_v9: vegetacion, lluvia_gpm_v9: lluviaGpm, lluvia_era5_v9: lluviaEra5};
Object.keys(tareas).forEach(function (nombre) {
  Export.image.toDrive({
    image: tareas[nombre].clip(MUNDO),
    description: 'atlas_analog_' + nombre, folder: 'AtlasAnalog',
    fileNamePrefix: 'atlas_analog_' + nombre,
    region: MUNDO, crs: 'EPSG:4326', crsTransform: GRILLA, maxPixels: 1e9
  });
});
