
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
    where find_tab.column_name = '{geom_table}'
    '''
    schema_temp = '''
    CREATE TABLE "{tablename}" (
        "id" serial NOT NULL PRIMARY KEY,
        {sql_columns}
        "map_id" INTEGER REFERENCES maps(id)
    );
    {sql_index}
    '''
    geom_schema_str = '        "{geom_table}" geometry({geom_type},{epsg_code}),'
    prop_schema_str = '        "{prop_key}" {prop_item},'
    geom_index_temp = '''
    CREATE INDEX {tablename}_geom_idx
        ON "{tablename}"
        USING gist
        (geom);
    '''

    #----------------------------------------------------------------------
    def __init__(self, layer_name):
        """Constructor"""
       
        self.layer_name = layer_name
        
        self.engine = create_engine_db('geo')
        self.connect = self.engine.connect()
        self.get_tabs_cols()
    
    def get_tabs_cols(self):
        self.tabs_cols = {}
        tabs_cols_sql = self.tabs_cols_sql.format(geom_table=self.geom_table)
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
    
    def create_table(self, geom, properties):
        print(geom, properties)

    def upate_table(self, properties):
        print(properties)
