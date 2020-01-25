from Models.Database import Database


def create_thermostat_database(read_only):
    db_file = 'Thermostat.db'

    sql_create = """CREATE TABLE IF NOT EXISTS stats (
                            time integer PRIMARY KEY,
                            sensor_temperature real NOT NULL,
                            target_temperature real NOT NULL,
                            outside_temperature real,
                            boiler_on integer NOT NULL
                        );"""

    sql_write = ''' INSERT INTO stats(time,sensor_temperature,target_temperature,boiler_on,outside_temperature) 
                    VALUES(?,?,?,?,?) '''

    sql_read = "SELECT time,sensor_temperature,target_temperature,boiler_on FROM stats WHERE time>=? AND time<?"

    return Database(read_only, db_file, sql_create, sql_read, sql_write)


def create_house_database(read_only):
    db_file = 'House.db'

    sql_create = """CREATE TABLE IF NOT EXISTS stats (
                            time integer PRIMARY KEY,
                            sensor_temperature real NOT NULL,
                            target_temperature real NOT NULL,
                            outside_temperature real,
                            boiler_on integer NOT NULL
                        );"""

    sql_write = ''' INSERT INTO stats(time,sensor_temperature,target_temperature,boiler_on,outside_temperature) 
                    VALUES(?,?,?,?,?) '''

    sql_read = "SELECT time,sensor_temperature,target_temperature,boiler_on FROM stats WHERE time>=? AND time<?"

    return Database(read_only, db_file, sql_create, sql_read, sql_write)
