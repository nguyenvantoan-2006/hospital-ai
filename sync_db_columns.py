# sync_db_columns.py
from database import engine, Base
import models
from sqlalchemy import text

def sync_schema():
    with engine.connect() as conn:
        for table_name, table in Base.metadata.tables.items():
            try:
                res = conn.execute(text(f"DESCRIBE `{table_name}`")).fetchall()
                existing_cols = {row[0] for row in res}
                for col in table.columns:
                    if col.name not in existing_cols:
                        print(f"Adding missing column: {table_name}.{col.name}")
                        col_type = col.type.compile(engine.dialect)
                        nullable = "NULL" if col.nullable else "NOT NULL"
                        default = ""
                        if col.default is not None and col.default.arg is not None:
                            val = col.default.arg
                            if isinstance(val, str):
                                default = f" DEFAULT '{val}'"
                            elif isinstance(val, (int, float)):
                                default = f" DEFAULT {val}"
                        elif not col.nullable:
                            if "VARCHAR" in str(col_type).upper() or "TEXT" in str(col_type).upper():
                                default = " DEFAULT ''"
                            elif "INT" in str(col_type).upper() or "FLOAT" in str(col_type).upper():
                                default = " DEFAULT 0"
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col.name}` {col_type} {nullable}{default}"
                        print("  Executing:", sql)
                        conn.execute(text(sql))
                        conn.commit()
            except Exception as e:
                print(f"Error checking table {table_name}:", e)
        print("Schema sync completed!")

if __name__ == "__main__":
    sync_schema()
