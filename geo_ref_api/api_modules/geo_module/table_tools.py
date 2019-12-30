
from geo_ref_api import config
from geo_ref_api.modules_factory import create_engine_db, ExceptionDepend


########################################################################
class GeoTable(object):
    """"""

    geom_table = 'geom'
    
    pytype2pgtype = {
        "int": "int4",
        "float": "float4",
        "str": "text",
        "bool": "bool",
        "dict": "json", 
    }

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
    --where find_tab.column_name = '{geom_table}'
    '''
    schema_temp = '''
    CREATE TABLE "{tablename}" (
        "id" serial NOT NULL PRIMARY KEY,
        {sql_columns}
        "{geom_table}" geometry({geom_type},{epsg_code})
    );
    CREATE INDEX {tablename}_geom_idx
        ON "{tablename}"
        USING gist
        ({geom_table});
    '''
    prop_schema_str = '        "{prop_key}" {prop_item},'

    #----------------------------------------------------------------------
    def __init__(self, layer_name):
        """Constructor"""
       
        self.layer_name = layer_name
        
        self.engine = create_engine_db('geo')
        self.connect = self.engine.connect()
        self.get_tabs_cols()
    
    def get_tabs_cols(self):
        self.tabs_cols = {}
        tabs_cols_sql = self.tabs_cols_sql.format(geom_table=config.GeomTablename)
        for tab in self.connect.execute(tabs_cols_sql).fetchall():
            arg_list = []
            for index in range(len(tab[1])):
                arg_list.append((tab[1][index], tab[2][index]))
            self.tabs_cols[tab[0]] = arg_list

    def type2pg(self, data):
        if isinstance(data, (list, tuple)):
            array_types = set([set(my) for my in data])
            if len(array_types) == 1:
                array_pytype = array_types.pop()
                return '_{}'.format(
                    self.pytype2pgtype.get(array_pytype.__name__, None)
                )
            else:
                return None
        else:
            return self.pytype2pgtype.get(type(data).__name__, None)
    
    def prop2pg(self, properties):
        pg_props = {}
        for key in properties.keys():
            if not properties[key]:
                return None
            elif isinstance(properties[key], (list, tuple)):
                pg_type = self.pytype2pgtype.get(properties[key][0], None)
                if pg_type:
                    pg_type = '_{}'.format(pg_type)
                else:
                    return None
            else:
                pg_type = self.pytype2pgtype.get(properties[key], None)
                if not pg_type:
                    return None
            pg_props[key] = pg_type
        return pg_props
    
    def create_table(self, geom, properties):
        if self.layer_name in self.tabs_cols:
            return 409, {
                "error": "Layer Table '{}' alredy created!".format(self.layer_name)
            }
        
        pg_props = self.prop2pg(properties)
        sql_columns = []
        for prop_key in pg_props.keys():
            sql_columns.append(
                self.prop_schema_str.format(
                    prop_key=prop_key,
                    prop_item=pg_props[prop_key], 
                )
            )
        sql_schema = self.schema_temp.format(
            tablename=self.layer_name,
            geom_table=config.GeomTablename, 
            geom_type=geom, 
            epsg_code=config.EpsgCode, 
            sql_columns='\n'.join(sql_columns),
        )
        self.connect.execute(sql_schema)
        self.get_tabs_cols()
        return 200, {}

    def upate_table(self, properties):
        print(self.prop2pg(properties))
        return 200, {}
