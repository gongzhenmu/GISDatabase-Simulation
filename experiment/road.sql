WITH segments AS (
SELECT osm_id, ST_MakeLine(lag((pt).geom, 1, NULL) OVER (PARTITION BY osm_id ORDER BY osm_id, (pt).path), (pt).geom) AS geom
  FROM (SELECT osm_id, ST_DumpPoints(way) AS pt FROM planet_osm_line) AS dumps)
SELECT id, name, highway, ST_StartPoint(geom::geometry) as u, ST_EndPoint(geom::geometry) as v, geom, ST_Length(geom::geography)/1609.344 AS distance 
FROM segments JOIN (select osm_id as id, name, highway from planet_osm_line) as lines on lines.id = segments.osm_id 
WHERE geom IS NOT null and highway is not null
;
