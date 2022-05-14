# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from typing import Any
from core.coredataclasses import DatabaseFieldDefinition
from core.coredatabase import CoreDatabase

def is_plugin_in_db(plugin_id: str) -> bool:
    print(f"Checking if platform with id '{plugin_id} is in database...")
        
    plugin_exists_query = f"SELECT count(name) FROM sqlite_master WHERE type = 'table' AND name = ?;"
    parameters = (plugin_id + "_data",)

    cursor = CoreDatabase.instance()._connection.cursor()
    return cursor.execute(plugin_exists_query, parameters).fetchone()[0] == 1

# Initialises plugin table in database and provides plugin with database table name
def create_plugin_table(plugin_table_name: str, data_fields: list[DatabaseFieldDefinition]):
    if data_fields.count == 0 or is_plugin_in_db(plugin_table_name):
        return
    
    print(f"Creating database table {plugin_table_name}")
       
    create_query = f'''CREATE TABLE IF NOT EXISTS {plugin_table_name} 
        (
            id      INTEGER     PRIMARY KEY AUTOINCREMENT,
        '''
    # Plugins provide data field definitions as a tuple of tuples. These inner tuples contain three elements.
    # 1. Field name | 2. Field data type | 3. Field constraints (i.e. uniqueness)
    for (field_name, field_type, field_constraints) in data_fields:
        create_query += f"{field_name} {field_type} {field_constraints},"
    create_query = create_query[:-1] + ");" # Chop off last comma and finish query

    cursor = CoreDatabase.instance()._connection.cursor()
    cursor.execute(create_query)
    CoreDatabase.instance()._connection.commit()
    

def delete_plugin_table(plugin_table_name: str):
    query = f"DROP TABLE IF EXISTS {plugin_table_name};"

    cursor = CoreDatabase.instance()._connection.cursor()
    cursor = cursor.execute(query)
    CoreDatabase.instance()._connection.commit()


def plugin_data(plugin_table_name: str) -> list[dict[Any, Any]]:
    query = f"SELECT * FROM {plugin_table_name};"

    cursor = CoreDatabase.instance()._connection.cursor()
    cursor = cursor.execute(query)
    query_results = cursor.fetchall()
    return_data = []

    for row in query_results:
        column_names = [description[0] for description in cursor.description]
        row_values = [value for value in row]
        row_as_dict = dict(zip(column_names, row_values))
        return_data.append(row_as_dict)

    return return_data


def add_plugin_data(plugin_table_name: str, data: dict[str, Any]):
    if len(data) == 0:
        return

    field_names = CoreDatabase.instance().table_fields(plugin_table_name)
    values_to_insert = []
    insert_query = f"INSERT INTO {plugin_table_name} VALUES ("

    # We want to iterate through the field names as we need to insert in order.
    # The table_fields gives us that, and we just insert the provided data values
    # (or empty values) into the values_to_insert to get everything right.
    for name in field_names:
        if name in data.keys():
            values_to_insert.append(data[name])
        else:
            values_to_insert.append(None)    
        insert_query += "?, "
    insert_query = insert_query[:-2] + ");" # Chop off last comma

    cursor = CoreDatabase.instance()._connection.cursor()
    cursor.execute(insert_query, values_to_insert)
    CoreDatabase.instance()._connection.commit()

    return cursor.lastrowid


def update_plugin_data(plugin_table_name: str, data_id: int, data: dict[str, Any]):
    if len(data) == 0:
        return

    update_query = f"UPDATE {plugin_table_name} SET "
    update_query_end = f" WHERE id = ?;"

    for field_name in data.keys():
        update_query += f"{field_name} = ?, "
    
    update_query = update_query[:-2] + update_query_end
    parameters = (*data.values(), data_id)

    cursor = CoreDatabase.instance()._connection.cursor()
    cursor.execute(update_query, parameters)
    CoreDatabase.instance()._connection.commit()


def delete_plugin_data(plugin_table_name: str, data_id: int):
    delete_query = f"DELETE FROM {plugin_table_name} WHERE id = ?"
    parameters = (data_id,)

    cursor = CoreDatabase.instance()._connection.cursor()
    cursor.execute(delete_query, parameters)
    CoreDatabase.instance()._connection.commit()