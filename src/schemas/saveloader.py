import asqlite, asyncio

"""SQLite Notes:
1. Data Types
NULL - None
INTEGER - int
STRING - str
REAL - decimals
INTEGER - any 

1.1 Data Type Requirements
NN (Not Null) - The data must not be empty.
PK (Primary key) - Self-Explanatory.
"""

async def check_table(path: str, table: str):
    async with asqlite.connect(path) as conn, conn.cursor() as db:
        # Make table for server
        await db.execute(f"""CREATE TABLE IF NOT EXISTS '{table}' (
        "id"	                    INTEGER NOT NULL,
        "points"	                INTEGER NOT NULL DEFAULT 0,
        "shift_amount"	            INTEGER NOT NULL DEFAULT 0,
        "shift_duration_seconds"	INTEGER NOT NULL DEFAULT 0,
        "shift_status"              INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY("id") ON CONFLICT FAIL
        );""")

        # make table for server info
        await db.execute("""CREATE TABLE IF NOT EXISTS 'server_info' (
        "id"                        INTEGER NOT NULL UNIQUE,
        "startup_message_id"        INTEGER,
        "last_startup_message_id",  INTEGER,
        PRIMARY KEY("id") ON CONFLICT FAIL
        );""")

async def edit(path: str, table: str, value_column: str, ref_column: str, ref_value, value):
    """
    Edits a existing data to a database file.
    
    Args:
        path (str): The path of the database file.
        table (str): The table that the data will is in.
        value_column (str): The data's column
        ref_column (str): The refrence data's column
        ref_value (any): The refrence data
        value (any): The data you want to insert.
    """

    async with asqlite.connect(path) as conn, conn.cursor() as db:
        code = f"UPDATE '{table}' SET {value_column} = ? WHERE {ref_column} = ?"
        "UPDATE server_info SET prefix = bt WHERE name = bot-test"
        try:
            await db.execute(code, (value,ref_value))
        except Exception as e: print(e)
        await conn.commit()

async def add(path: str, table: str, value_column: str, value):
    """
    Adds data to a database file.
    
    Args:
        path (str): The path of the database file.
        table (str): The table that the data will be in.
        value_column (str): The data's name.
        value (any): The data you want to insert.
    """

    async with asqlite.connect(path) as conn, conn.cursor() as db:
        code = f"INSERT OR REPLACE INTO '{table}' ({value_column}) VALUES(?)"
        "INSERT OR REPLACE INTO 'server_info' ('name') VALUES('bot test')"
        try:
            await db.execute(code, (value,)) 
        except Exception as e: print(e)
        await conn.commit()

async def check_data(path: str, table: str, value_column: str, ref_column: str, ref_value: any) -> bool:
    """
    Checks whether data exists from a database file.
    
    Args:
        path (str): The path of the database file.
        table (str): The table that the data is in.    
        value_column (str): The data's column
        ref_column (str): The refrence data's column
        ref_value (any): The refrence data
    
    Returns: 
        bool: Data exists/doesn't
    """

    async with asqlite.connect(path) as conn, conn.cursor() as db:
        code = f"""	
        SELECT EXISTS (
            SELECT {value_column} FROM '{table}' 
            WHERE {ref_column} = ?
            -- keep the func below for later
            --HAVING ? NOT NULL
            LIMIT 1
        );"""
        await db.execute(code, (ref_value,))
        data = await db.fetchone()
        
        match data[0]:
            case 1: check = await load(path, table, value_column, ref_column, ref_value)
            case 0: return False
 
        match check:
            case 0 | None: return False
            case _: return True

async def load(path: str, table: str, value_column: str, ref_column: str, ref_value: any) -> any:
    """
    Gets data from a database file.
    
    Args:
        path (str): The path of the database file.
        table (str): The table that the data is in.    
        value_column (str): The data's column
        ref_column (str): The refrence data's column
        ref_value (any): The refrence data
    
    Returns: 
        any: The data
    """

    async with asqlite.connect(path) as conn, conn.cursor() as db:
        code = f"""
            SELECT {value_column} FROM '{table}' WHERE {ref_column} = ? LIMIT 1
        """
        await db.execute(code, (ref_value,))
        data = await db.fetchone()
        
        if data == None:
            data = [0]

    return data[0]
    
if __name__ == "__main__":
    print(asyncio.run(check_data("./save.db", "server_info", "last_startup_message_id", "id", 910687741380005978)))
