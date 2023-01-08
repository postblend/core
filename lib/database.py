# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from typing import Any

from core.database.databasecontroller import DatabaseController, USERS_TABLE

DatabaseFieldDefinition = tuple[str, str, str]

"""
Checks if there are any tables in the database created by the plugin with the provided id.
Returns a simple true/false.

Arguments:

    plugin_id:              Integer representing the plugin's id.
"""
# TODO: Rewrite this, we need a table containing the ids of tables creating by plugins
def is_plugin_in_db(plugin_id: str) -> bool:
    print(f"Checking if platform with id '{plugin_id}' is in database...")
        
    plugin_exists_query = f"SELECT count(name) FROM sqlite_master WHERE type = 'table' AND name = ?;"
    parameters = (plugin_id + "_data",)

    cursor = DatabaseController.instance()._connection.cursor()
    return cursor.execute(plugin_exists_query, parameters).fetchone()[0] == 1


"""
Creates a database table according to the details provided by the plugin.

All tables will get an 'id' field by default. This is an auto-incrementing integer which functions as the
table's primary key. Do not remove this field!

Arguments:

    plugin_table_name:      String representing the name of the table to be created

    data_fields:            List of DatabaseFieldDefinitions (3-string tuples) which should detail the 
                            fields of the database table.
                      
                            String1 represents the field name (e.g. "username")
                            String2 represents the field type (e.g. TEXT)
                            String3 represents the field constraints (e.g. NOT NULL PRIMARY KEY)
"""
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

    cursor = DatabaseController.instance()._connection.cursor()
    cursor.execute(create_query)
    DatabaseController.instance()._connection.commit()
    

"""
Delete the table from the database with the provided table name.
It also ensures that no core table is deleted.

Arguments:

    plugin_table_name:      String representing the name of the table to be created
"""
# TODO: Ensure that this method can only delete tables created by the plugin itself
def delete_plugin_table(plugin_table_name: str):
    if plugin_table_name == USERS_TABLE:
        print("You are not allowed to delete the users table.")
        return

    print(f"Deleting database table {plugin_table_name} if it exists")

    query = f"DROP TABLE IF EXISTS {plugin_table_name};"

    cursor = DatabaseController.instance()._connection.cursor()
    cursor = cursor.execute(query)
    DatabaseController.instance()._connection.commit()


"""
Retrieve the data stored in the table with the provided name.

This data is returned in the form of a list of dicts. Each dict represents a row, and contains that row's
values -- the dict key is the table field name, and the dict value is the row's value for that field. 

E.g.: in a table with an id and username fields, the returned list would contain:

[ {"id": 1, "username": "user1"}, {"id": 2, "username": "user2"}, {"id": 3, "username": "user3"} ]

Arguments:

    plugin_table_name:      String representing the name of the table the data will be fetched from
"""
def plugin_data(plugin_table_name: str) -> list[dict[Any, Any]]:
    query = f"SELECT * FROM {plugin_table_name};"

    cursor = DatabaseController.instance()._connection.cursor()
    cursor = cursor.execute(query)
    query_results = cursor.fetchall()
    return_data = []

    for row in query_results:
        column_names = [description[0] for description in cursor.description]
        row_values = [value for value in row]
        row_as_dict = dict(zip(column_names, row_values))
        return_data.append(row_as_dict)

    return return_data


"""
Similarly to plugin_data, this retrieves the data stored in the table with the provided name.
This method, however, only returns the row with the provided row_id.

The return type is the same (see above for details).

Arguments:

    plugin_table_name:    String representing the name of the table the data will be fetched from

    row_id:               The ID of the specific row's data to be fetched
"""
def plugin_data_row(plugin_table_name: str, row_id: int) -> dict[Any, Any]:
    query = f"SELECT * FROM {plugin_table_name} WHERE id = ?;"
    parameters = (row_id,)

    cursor = DatabaseController.instance()._connection.cursor()
    cursor = cursor.execute(query, parameters)
    query_result = cursor.fetchone()

    if query_result:
        column_names = [description[0] for description in cursor.description]
        row_values = [value for value in query_result]
        row_as_dict = dict(zip(column_names, row_values))
        return row_as_dict
    
    return dict()

"""
Similarly to plugin_data_row, this retrieves the data stored in the table with the provided name.
This method, however, returns all the rows in which the field matches the value provided.

The return type is the same (see above for details).

Arguments:

    plugin_table_name:    String representing the name of the table the data will be fetched from

    field_name:           Name of the field we want to search in

    field_value:                The value we want to match

Returns:

A list of dictionaries containing the data from the matched rows.

TODO
* Add version that returns records where multiple fields match multiple values
"""
def plugin_data_values(plugin_table_name: str, field_name: str, field_value: str) -> list[dict[Any, Any]]:
    query = f"SELECT * FROM {plugin_table_name} WHERE {field_name} = ?;"
    parameters = (field_value,)

    cursor = DatabaseController.instance()._connection.cursor()
    cursor = cursor.execute(query, parameters)
    query_results = cursor.fetchall()
    return_data = []

    for row in query_results:
        column_names = [description[0] for description in cursor.description]
        row_values = [value for value in row]
        row_as_dict = dict(zip(column_names, row_values))
        return_data.append(row_as_dict)

    return return_data


"""
Add a new row of data to the database table with the provided name.

Arguments:

    plugin_table_name:      String representing the name of the table the data will be inserted into

    data:                   A dictionary containing the data to be inserted.

                            The dictionary's keys should be the field names, and the values what is
                            to be inserted. (e.g. {"username": "user1", "name": "First User"}).

                            You will need to provide values according to the field constraints you
                            have specified, i.e. NOT NULL fields will need to have values provided 
                            or the process will fail.

                            You do not need to worry about providing the fields in the correct 
                            order.

                            Do not insert a value for the "id" field manually.

"""
def add_plugin_data(plugin_table_name: str, data: dict[str, Any]):
    if len(data) == 0:
        return

    field_names = DatabaseController.instance().table_fields(plugin_table_name)
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

    cursor = DatabaseController.instance()._connection.cursor()
    cursor.execute(insert_query, values_to_insert)
    DatabaseController.instance()._connection.commit()

    return cursor.lastrowid


"""
Update a data row in the database table with the provided name.

Arguments:

    plugin_table_name:      String representing the name of the table the data will be inserted into

    data_id:                Integer representing the specific data row

    data:                   A dictionary containing the data to be inserted.

                            The dictionary's keys should be the field names, and the values what is
                            to be inserted. (e.g. {"username": "user1", "name": "First User"}).

                            You will need to provide values according to the field constraints you
                            have specified, i.e. NOT NULL fields will need to have values provided 
                            or the process will fail.

                            You do not need to worry about providing the fields in the correct 
                            order.

                            Do not insert a value for the "id" field manually.
"""
def update_plugin_data(plugin_table_name: str, data_id: int, data: dict[str, Any]):
    if len(data) == 0:
        return

    update_query = f"UPDATE {plugin_table_name} SET "
    update_query_end = f" WHERE id = ?;"

    for field_name in data.keys():
        update_query += f"{field_name} = ?, "
    
    update_query = update_query[:-2] + update_query_end
    parameters = (*data.values(), data_id)

    cursor = DatabaseController.instance()._connection.cursor()
    cursor.execute(update_query, parameters)
    DatabaseController.instance()._connection.commit()


"""
Delete a data row in the database table with the provided name.

Arguments:

    plugin_table_name:      String representing the name of the table the data will be inserted into

    data_id:                Integer representing the specific data row
"""
def delete_plugin_data(plugin_table_name: str, data_id: int):
    delete_query = f"DELETE FROM {plugin_table_name} WHERE id = ?"
    parameters = (data_id,)

    cursor = DatabaseController.instance()._connection.cursor()
    cursor.execute(delete_query, parameters)
    DatabaseController.instance()._connection.commit()
