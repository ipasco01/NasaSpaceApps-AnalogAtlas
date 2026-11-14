// Atlas Analog · earth_engine_v4.js
// v0.4 · 2026-11-14 · Isabelita (equipo Ctrl Z)
// Pegar en code.earthengine.google.com y presionar Run. Exporta la Tierra a Google Drive (carpeta AtlasAnalog).
// Relieve global (ETOPO1), cobertura 2022, temperatura con Aqua. La pendiente se calcula después en
// data-pipeline/tif_a_tabla.py, igual que para la Luna y Marte.
var INICIO = '2018-01-01';
var FIN    = '2023-12-31';

var elevacion = ee.Image('NOAA/NGDC/ETOPO1').select('ice_surface').rename('elevacion');

var lst = ee.ImageCollection('MODIS/061/MYD11A2').filterDate(INICIO, FIN);
var tempDia   = lst.select('LST_Day_1km').mean().multiply(0.02).subtract(273.15).rename('temp_dia');
var tempNoche = lst.select('LST_Night_1km').mean().multiply(0.02).subtract(273.15).rename('temp_noche');
var rangoTermico = tempDia.subtract(tempNoche).rename('rango_termico');
var permafrost = tempDia.add(tempNoche).divide(2).lt(0).rename('permafrost_proxy');

var lluvia = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07')
  .filterDate(INICIO, FIN).select('precipitation')
  .median().multiply(24 * 365).rename('lluvia');

var ndvi = ee.ImageCollection('MODIS/061/MOD13A3')
  .filterDate(INICIO, FIN).select('NDVI').mean().multiply(0.0001).rename('ndvi');

var nieve = ee.ImageCollection('MODIS/061/MOD10A1')
  .filterDate(INICIO, FIN).select('NDSI_Snow_Cover').mean().rename('nieve');

var polvo = ee.ImageCollection('NASA/GSFC/MERRA/aer/2')
  .filterDate('2022-01-01', '2023-01-01').select('DUEXTTAU').mean().rename('polvo');

var cobertura = ee.ImageCollection('MODIS/061/MCD12Q1')
  .filterDate('2022-01-01', '2023-01-01').first().select('LC_Type1');
var arido = cobertura.eq(16).rename('arido');
var hielo = cobertura.eq(15).rename('hielo');
var tierraFirme = cobertura.neq(17);

var capas = ee.Image.cat([elevacion, tempDia, tempNoche, rangoTermico,
                          lluvia, ndvi, arido, nieve, hielo, permafrost, polvo])
  .toFloat().updateMask(tierraFirme);

// Comprobación: las dos deben mostrar números, no null
print('Piura', capas.reduceRegion({reducer: ee.Reducer.first(),
  geometry: ee.Geometry.Point([-80.6, -5.6]), scale: 27830}));
print('Siberia 72N', capas.reduceRegion({reducer: ee.Reducer.first(),
  geometry: ee.Geometry.Point([110, 72]), scale: 27830}));

Export.image.toDrive({
  image: capas,
  description: 'atlas_analog_global_025_v4',
  folder: 'AtlasAnalog',
  fileNamePrefix: 'atlas_analog_global_025_v4',
  region: ee.Geometry.Rectangle([-180, -90, 180, 90], null, false),
  crs: 'EPSG:4326',
  crsTransform: [0.25, 0, -180, 0, -0.25, 90],
  maxPixels: 1e9
});
