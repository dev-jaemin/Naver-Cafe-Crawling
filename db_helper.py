from psycopg2 import pool
from psycopg2 import extras


class ConnectionPool:
    """
    PostgreSQL Connection Pool 클래스
    """
    __pool = None

    def __init__(self, minconn: int, maxconn: int, **kwargs):
        """
        Connection Pool 객체 초기화
        :param minconn: 최소 연결 수
        :param maxconn: 최대 연결 수
        :param kwargs: PostgreSQL 연결 설정
        """
        self.minconn = minconn
        self.maxconn = maxconn
        self.kwargs = kwargs
        self._create_pool()

    def _create_pool(self):
        if not self.__pool:
            try:
                self.__pool = pool.SimpleConnectionPool(
                    self.minconn, self.maxconn, **self.kwargs
                )
            except Exception as e:
                print("Error: ", e)

    def get_connection(self):
        if self.__pool == None:
            self._create_pool()

        return self.__pool.getconn()

    def put_connection(self, connection):
        self.__pool.putconn(connection)

    def close_all_connections(self):
        self.__pool.closeall()

    def insert_data(self, table_name: str, columns: list, data: list):
        conn = self.get_connection()
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        columns_str = ','.join(columns)

        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES %s"

        try:
            extras.execute_values(cursor, insert_query, data)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("Error: ", e)
        finally:
            cursor.close()
            self.put_connection(conn)
