import duckdb
import pandas as pd


def sql(df: pd.DataFrame, query: str):

    connection = duckdb.connect()

    connection.register("df", df)

    result = connection.execute(query).df()

    connection.close()

    return result
