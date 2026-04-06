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

async def edit(path: str, table: str, value_index: str, value):
    """
    Edits a existing data to a database file.
    
    Args:
        path (str): The path of the database file.
        table (str): The table that the data will is in.
        value_index (str): The data's name.
        value (any): The data you want to insert.
    """

    async with asqlite.connect(path) as conn, conn.cursor() as db:
        code = f"UPDATE OR ABORT {table} SET value = ? WHERE id = ?"
        await db.execute(code, value, value_index)
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
        code = f"INSERT OR ABORT INTO {table} (id, value) VALUES(?,?)"
        await db.execute(code, (value_index, value))     
        await conn.commit()

async def load(path: str, table: str, column: str, value_index: str) -> any:
    """
    Loads data from a database file.
    
    Args:
        path (str): The path of the database file.
        table (str): The table that the data is in.
        column (str): The column the data is in.
        value_index (str): The data's name.
        
    Returns: 
        any: The data itself.
    """

    async with asqlite.connect(path) as conn, conn.cursor() as db:
        code = f"SELECT {column} FROM {table} WHERE id = ?"
        "SELECT points FROM bot_test WHERE id = 1233456667"
        await db.execute(code, (value_index))
        data = await db.fetchone()

    if data is not None:
        return data[0]
    
if __name__ == "__main__":
    print(asyncio.run(load("../save.db", "social_credit", "catamapp")))