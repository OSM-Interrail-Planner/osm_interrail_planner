from .logs import die
import sqlalchemy as sql
import pandas as pd


class DBController:
    def __init__(self, host: str, port: str, database: str, username: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.uri = f"postgres+psycopg2://{username}:{password}@{host}:{port}/{database}"

    def select_data(self, query: str) -> pd.DataFrame:
        """This functions abstracts the `SELECT` queries

        Args:
            query (str): the select query to be executed

        Returns:
            pd.DataFrame: the selection
        """
        try:
            con = sql.create_engine(self.uri)
            df = pd.read_sql(query, con)
        except Exception as e:
            die(f"select_data: {e}")
        return df

    def insert_data(self, df: pd.DataFrame, schema: str, table: str, chunksize: int=100) -> None:
        """This function abstracts the `INSERT` queries

        Args:
            df (pd.DataFrame): dataframe to be inserted
            schema (str): the name of the schema
            table (str): the name of the table
            chunksize (int): the number of rows to insert at the time
        """
        try:
            engine = sql.create_engine(self.uri)
            print("CREATE_ENGINE")
            with engine.connect() as con:
                tran = con.begin()
                df.to_sql(
                    name=table, schema=schema,
                    con=con, if_exists="append", index=False,
                    chunksize=chunksize, method="multi"
                )
                tran.commit()
        except Exception as e:
            tran.rollback()
            die(f"{e}")
