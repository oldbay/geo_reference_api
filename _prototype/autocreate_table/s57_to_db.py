import os
import gdal, ogr
import json

from sqlalchemy import create_engine

#gdal.SetConfigOption('OGR_S57_OPTIONS', 'SPLIT_MULTIPOINT=ON')
gdal.SetConfigOption('OGR_S57_OPTIONS', 'RETURN_PRIMITIVES=ON')
gdal.SetConfigOption('OGR_S57_OPTIONS', 'RETURN_LINKAGES=ON')
gdal.SetConfigOption('OGR_S57_OPTIONS', 'LNAM_REFS=ON')
gdal.SetConfigOption('OGR_S57_OPTIONS', 'RECODE_BY_DSSI=ON')

########################################################################
class MapLoader(object):
    """"""
    
    debug = True
        
    pytype2pgtype = {
        "null": 'int2',
        "int": "int4",
        "float": "float4",
        "str": "text",
    }
    
    not_geom_prefix = 'NotGeo'
    maps_table_sql = '''
    CREATE TABLE IF NOT EXISTS "maps" (
        "id" serial NOT NULL PRIMARY KEY,
        "name" VARCHAR(256) NOT NULL UNIQUE,
        "epsg" INTEGER
    );
    '''
    tabs_cols_sql = '''
    select find_tab.table_name as tabs,
        array(
            select column_name::text
            from information_schema.columns
            where table_name = find_tab.table_name
        ) as cols,
        array(
            select udt_name::text
            from information_schema.columns
            where table_name = find_tab.table_name
        ) as typs
    from information_schema.columns as find_tab
    where find_tab.column_name = 'map_id'
    '''
    schema_temp = '''
    CREATE TABLE "{tablename}" (
        "id" serial NOT NULL PRIMARY KEY,
        {sql_columns}
        "map_id" INTEGER REFERENCES maps(id)
    );
    {sql_index}
    '''
    geom_schema_str = '        "geom" geometry({geom_type}),'
    prop_schema_str = '        "{prop_key}" {prop_item},'
    geom_index_temp = '''
    CREATE INDEX {tablename}_geom_idx
        ON "{tablename}"
        USING gist
        (geom);
    '''
    alter_col_add = 'alter table "{tablename}" add column "{colname}" {coltype};'
    alter_col_type = '''
        alter table "{tablename}" drop column "{colname}";
        alter table "{tablename}" add column "{colname}" {coltype};
    '''
    query_map_id = '''
    select id
    from "maps"
    where name='{mapname}'
    '''
    insert_map = '''
    INSERT INTO maps(name)
        VALUES('{mapname}')
    ;
    '''
    update_map_epsg = '''
    UPDATE maps SET epsg={epsg}
        WHERE id = {map_id}
    '''
    delete_map = '''
    DELETE FROM maps
        WHERE id = {map_id}
    '''
    insert_prop = '''
    INSERT INTO "{tablename}"({prop_keys})
        VALUES({prop_items})
    ;
    '''

    #----------------------------------------------------------------------
    def __init__(self, map_file, db_path, epsg=None):
        """Constructor"""
        
        self.epsg = epsg
        self.mapname = os.path.basename(map_file)
        self.map_id = None
        
        self.engine = create_engine(db_path)
        self.connect = self.engine.connect()
        self.connect.execute(self.maps_table_sql)
        self.get_tabs_cols()
   
        self.src_ds = ogr.Open(map_file)
        self.set_map()
    
    def get_tabs_cols(self):
        self.tabs_cols = {}
        for tab in self.connect.execute(self.tabs_cols_sql).fetchall():
            arg_list = []
            for index in range(len(tab[1])):
                arg_list.append((tab[1][index], tab[2][index]))
            self.tabs_cols[tab[0]] = arg_list
    
    def type2pg(self, data):
        if not data:
            return self.pytype2pgtype["null"]
        elif isinstance(data, (list, tuple)):
            return '_{}'.format(self.pytype2pgtype[type(data[0]).__name__])
        else:
            return self.pytype2pgtype[type(data).__name__]

    def set_map(self):
        self.map_id = self.connect.execute(
            self.query_map_id.format(mapname=self.mapname)
        ).fetchone()
        if not self.map_id:
            self.connect.execute(
                self.insert_map.format(
                    mapname=self.mapname,
                    epsg=self.epsg
                )
            )
            self.map_id = int(self.connect.execute(
                self.query_map_id.format(mapname=self.mapname)
            ).fetchone()[0])
            for layer in self.src_ds:
                #  find epsg
                if not self.epsg:
                    srs = layer.GetSpatialRef()
                    if srs:
                        find_epsg = srs.GetAttrValue("AUTHORITY", 1)
                        if find_epsg:
                            self.epsg = int(find_epsg)
                            self.connect.execute(
                                self.update_map_epsg.format(
                                    epsg=self.epsg,
                                    map_id=self.map_id
                                )
                            )
                # features processing
                self.set_features(layer)
    
    def set_features(self, layer):
        layer_name = layer.GetName()
        for feature in layer:
            geojson = json.loads(feature.ExportToJson())
            
            # keys 
            prop_keys = ','.join([
                '"{}"'.format(my[0])
                for my
                in geojson['properties'].items()
            ])
            prop_keys += ',"map_id"'
            
            # items + paser
            prop_items_list = []
            for prop_it in geojson['properties'].items():
                pr_it = prop_it[-1]
                if not pr_it:
                    prop_items_list.append('NULL')
                elif isinstance(pr_it, str):
                    prop_items_list.append(
                        "'{}'".format(
                            repr(str(pr_it))[1: -1]
                                .replace('\\u', '|u') # fix unicode trmplate 
                                .replace('%', '%%') #  fix psycopg2 bug to %
                                .replace("'", "''") #  mask ' for postgres
                        )
                    )
                elif isinstance(pr_it, (list, tuple)):
                    lst = []
                    for var in pr_it:
                        if isinstance(var, (int, float)):
                            lst.append(str(var))
                        else:
                            lst.append("'{}'".format(var))
                    prop_items_list.append(
                        "ARRAY[{}]".format(','.join(lst))
                    )
                else:
                    prop_items_list.append(str(pr_it))
                    
            prop_items = ",".join(prop_items_list)
            prop_items += ",{}".format(self.map_id)
            
            # geometry & table name
            if geojson['geometry']:
                prop_keys += ',"geom"'
                prop_items += ',ST_SetSRID(ST_GeomFromGeoJSON(\'{0}\'),{1})'.format(
                    json.dumps(geojson['geometry']),
                    self.epsg
                )
                ogr_geometry = feature.GetGeometryRef()
                z_order = ''
                if ogr_geometry.Is3D():
                    z_order = 'Z'
                geom_prefix = geojson['geometry']['type'] + z_order
            else:
                geom_prefix = self.not_geom_prefix
            tablename = '{layer_name}_{geom_prefix}'.format(
                layer_name=layer_name,
                geom_prefix=geom_prefix
            )
            
            if self.debug:
                print( 
                    self.insert_prop.format(
                        tablename=tablename,
                        prop_keys=prop_keys,
                        prop_items=prop_items
                    )
                )

            # create or alter table schema
            if not self.tabs_cols.get(tablename, None):
                self.create_schema(tablename, geojson)
            else: 
                self.alter_schema(tablename, geojson)
            
            self.connect.execute(
                self.insert_prop.format(
                    tablename=tablename,
                    prop_keys=prop_keys,
                    prop_items=prop_items
                )
            )
    
    def create_schema(self, tablename, geojson):
        geom_type = tablename.split('_')[-1]
        if geom_type == self.not_geom_prefix:
            geom_type = None
        
        prop_keys = {
            key: self.type2pg(geojson['properties'][key])
            for
            key
            in
            list(geojson['properties'].keys())
        }
        
        sql_columns = []
        sql_index = ''
        if geom_type:
            sql_columns.append(
                self.geom_schema_str.format(geom_type=geom_type)
            )
            sql_index = self.geom_index_temp.format(
                tablename=tablename
            )
            
        for prop_key in prop_keys:
            sql_columns.append(
                self.prop_schema_str.format(
                    prop_key=prop_key,
                    prop_item=prop_keys[prop_key], 
                )
            )
        
        sql_schema = self.schema_temp.format(
            tablename=tablename,
            sql_columns='\n'.join(sql_columns),
            sql_index=sql_index
        )
        self.connect.execute(sql_schema)

        self.get_tabs_cols()
        
    
    def alter_schema(self, tablename, geojson):
        prop_keys = {
            key: self.type2pg(geojson['properties'][key])
            for
            key
            in
            list(geojson['properties'].keys())
        }
        old_columns = set(self.tabs_cols[tablename])
        new_columns = set(prop_keys.items())
        alter_ops = {}
        for col_diff in new_columns - old_columns:
            if col_diff[-1] != self.pytype2pgtype['null']:
                if col_diff[0] in dict(old_columns).keys():
                    if dict(old_columns)[col_diff[0]] == self.pytype2pgtype['null']:
                        alter_ops[col_diff[0]] = {
                            "query": self.alter_col_type,
                            "type": col_diff[-1]
                        }
                    else:
                        raise Exception(
                            "Error Alter type for Table '{0}': '{1}' to '{2}'".format(
                                col_diff[0],
                                dict(old_columns)[col_diff[0]],
                                col_diff[-1]
                            )
                        )
                else:
                    alter_ops[col_diff[0]] = {
                        "query": self.alter_col_add,
                        "type": col_diff[-1]
                    }
                
        if alter_ops:
            for op in alter_ops:
                sql_alter = alter_ops[op]['query'].format(
                    tablename=tablename,
                    colname=op,
                    coltype=alter_ops[op]['type']
                )
                self.connect.execute(sql_alter)
                
            self.get_tabs_cols()


if __name__ == "__main__":
    
    db_path = "postgresql+psycopg2://gis@localhost:5432/s57"
    #db_path = "postgresql+pg8000://gis:gis@localhost:5432/s57"
    s57_files = [
        's57/RU3NSK80.000', 
        #'s57/RU5O0KL0.000', 
        's57/RU5NTL01.000', 
        's57/RU2MFLB0.000',
        's57/RU4MALT0.000', 
        #'s57/RU4M9LS0.000', 
        #'s57/RU4MDL90.000', 
        #'s57/RU4MELF0.000', 
        #'s57/RU5M8M40.000', 
    ]
    for map_file in s57_files: 
        ml = MapLoader(map_file, db_path)