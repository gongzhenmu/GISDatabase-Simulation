select osm_id as id, name, amenity, shop, way as geom from planet_osm_point
where amenity  is not null or  shop is not null
;


