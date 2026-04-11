import asqlite, asyncio

"""SQLite Notes:
1. Data Types
NULL - None
INTEGER - int
STRING - str
REAL - decimals
BLOB - any 

1.1 Data Type Requirements
NN (Not Null) - The data must not be empty.
PK (Primary key) - Self-Explanatory.
"""

async def check_table(path: str, table: str):
    async with asqlite.connect(path) as conn, conn.cursor() as db:
        await db.execute(f"""CREATE TABLE IF NOT EXISTS "{table}" (
	"id"	INTEGER NOT NULL,
	"points"	INTEGER NOT NULL DEFAULT 0,
	"shifts"	INTEGER NOT NULL DEFAULT 0,
	"shift_duration_seconds"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("name") ON CONFLICT ABORT
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
        code = f"UPDATE OR REPLACE {table} SET {value_column} = ? WHERE {ref_column} = ?"
        "UPDATE OR REPLACE server_info SET prefix = bt WHERE name = bot-test"
        try:
            await db.execute(code, (value,ref_value))
        except Exception: pass
        await conn.commit()

async def add(path: str, table: str, value_index: str, value):
    """
    Adds data to a database file.
    
    Args:
        path (str): The path of the database file.
        table (str): The table that the data will be in.
        value_index (str): The data's name.
        value (any): The data you want to insert.
    """

    async with asqlite.connect(path) as conn, conn.cursor() as db:
        code = f"INSERT OR REPLACE INTO {table} ({value_index}) VALUES(?)"
        "INSERT OR REPLACE INTO 'server_info' ('name') VALUES('bot test')"
        try:
            await db.execute(code, (value,)) 
        except Exception: pass
        await conn.commit()

async def load(path: str, table: str, value_column: str, ref_column: str, ref_value: any) -> any:
    """
    Loads data from a database file.
    
    Args:
        path (str): The path of the database file.
        table (str): The table that the data is in.    
        value_column (str): The data's column
        ref_column (str): The refrence data's column
        ref_value (any): The refrence data
    
    Returns: 
        any: The data itself.
    """

    async with asqlite.connect(path) as conn, conn.cursor() as db:
        code = f"SELECT {value_column} FROM {table} WHERE {ref_column} = ?"
        "SELECT startup_message_id FROM server_info WHERE name = bot-test"
        try:
            await db.execute(code, (ref_value,))
            data = await db.fetchone()
        except Exception:
            raise KeyError("Data not found.")

    if data is not None:
        return data[0]
    
if __name__ == "__main__":
    print(asyncio.run(load("./save.db", "server_info", "startup_message_id", "name", "bot-test")))
