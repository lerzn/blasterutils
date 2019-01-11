import functools
import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from sqlalchemy.orm import scoped_session, sessionmaker


def not_read_only(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        if type(self).__readonly__:
            raise TypeError(f"{type(self).__name__}.__readonly__ is True, no editing allowed.")
        return func(self, *args, **kwargs)

    return wrapped


def make_sqlalchemy_engine(conn_params:dict):
    """
    Connection params with following keys: db_host, db_port, db_user, db_pwd, db_name.

    :param conn_params:
    :return:
    """
    connection_string = f"postgresql+psycopg2://{conn_params['db_host']}:{conn_params['db_pwd']}@{conn_params['db_host']}:{conn_params['db_port']}/{conn_params['db_name']}"
    engine = create_engine(
        connection_string,
        pool_size=30,
        max_overflow=50
    )
    del connection_string
    return engine

db = make_sqlalchemy_engine(YOUR_CONFIG_DICT)
Session = scoped_session(sessionmaker(db))

def create_session(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        session = Session()
        try:
            query_response = func(*args, session=session, **kwargs)
            return query_response
        except OperationalError as e:
            logging.warning(f'{e}')
        except Exception as e:
            logging.error(f'{e}')
            session.rollback()
            raise

    return inner


class ModelBase:
    """
    Class name must reflect the corresponding table name and end with 'Model'. For example
    if you table is called 'user', class must be named UserModel.
    """
    __tablename__: str
    __table_args__: dict
    __readonly__: bool = False

    @classmethod
    @create_session
    def find_by_id(cls, id_, session=None):
        return session.query(cls).get(id_)

    @classmethod
    @create_session
    def find_all(cls, count=False, session=None):
        logging.debug(f'{cls.__name__}: finding all')
        if not count:
            return session.query(cls).all()
        return session.query(cls).count()

    @classmethod
    @create_session
    def find_many_by_list_of_ids(cls, list_of_ids, *, session):
        if not list_of_ids:
            return None
        query = session.query(cls).filter(
            cls.id.in_(list_of_ids)
        )
        return query.all()

    @not_read_only
    def save_to_db(self):
        session = Session()
        session.add(self)
        try:
            session.commit()
        except Exception as e:
            logging.critical(f'SAVE TO DB FAILED: {e}')
            session.rollback()

    @not_read_only
    @create_session
    def delete_from_db(self, session=None):
        session.delete(self)
        session.commit()

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        if not self.id or not other.id:
            return False
        return self.id == other.id

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id if self.id else 'None'})"
