import functools
import logging

try:
    # pip install sqlalchemy
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.ext.declarative import declared_attr, declarative_base

    from sqlalchemy.orm import scoped_session, sessionmaker
except ModuleNotFoundError:
    pass


def not_read_only(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        if type(self).__readonly__:
            raise TypeError(f"{type(self).__name__}.__readonly__ is True, no editing allowed.")
        return func(self, *args, **kwargs)

    return wrapped


def make_sqlalchemy_engine(conn_params: dict):
    """
    Connection params with following keys: db_host, db_port, db_user, db_pwd, db_name.

    :param conn_params:
    :return:
    """
    connection_string = f"postgresql+psycopg2://{conn_params['db_user']}:" \
        f"{conn_params['db_pwd']}@{conn_params['db_host']}:{conn_params['db_port']}/{conn_params['db_name']}"
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
    def inner(self, *args, **kwargs):
        self.session = Session()
        try:
            return func(self, *args, **kwargs)
        except OperationalError as e:
            logging.warning(f'{e}')
        except Exception as e:
            logging.error(f'{e}')
            self.session.rollback()
            raise

    return inner


class ModelBase:
    """
    Class name must reflect the corresponding table name and end with 'Model'. For example
    if you table is called 'user', class must be named UserModel.
    """
    session = None

    @declared_attr
    def __tablename__(cls):
        if cls.__name__.find('Model') < 1:
            raise NameError(f"Illegal class name {cls.__name__}, must be {cls.__name__}Model")
        return cls.__name__[:cls.__name__.find('Model')].lower()

    __table_args__: dict
    __readonly__: bool = False

    @classmethod
    @create_session
    def find_by_id(cls, id_):
        return cls.session.query(cls).get(id_)

    @classmethod
    @create_session
    def find_all(cls, count=False):
        logging.debug(f'{cls.__name__}: finding all')
        if not count:
            return cls.session.query(cls).all()
        return cls.session.query(cls).count()

    @classmethod
    @create_session
    def find_many_by_list_of_ids(cls, list_of_ids):
        if not list_of_ids:
            return None
        query = cls.session.query(cls).filter(
            cls.id.in_(list_of_ids)
        )
        return query.all()

    # New save_to_db
    @not_read_only
    @create_session
    def save_to_db(self):
        # Check if a session for object is already open an utilize if it is.
        existing_session = self.session.object_session(self)
        try:
            logging.debug(f'Looking for existing session for {self}')
            existing_session.add(self)
            existing_session.commit()
            logging.info(f'Saved {self} using existing object session')
        except AttributeError:
            logging.info(f'Existing session not found. Saving {self} using new session')
            self.session.add(self)
            self.session.commit()
        except Exception as e:
            logging.critical(f'Save to DB failed: {e}')
            self.session.rollback()
            raise

    @not_read_only
    @create_session
    def delete_from_db(self):
        existing_session = self.session.object_session(self)
        if existing_session:
            self.session = existing_session
        self.session.delete(self)
        self.session.commit()

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        if not self.id or not other.id:
            return False
        return self.id == other.id

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id if self.id else 'None'})"


def _make_sql_alchemy_base(my_engine=None):
    mymetadata = MetaData()
    if my_engine:
        return declarative_base(cls=ModelBase, metadata=mymetadata, bind=my_engine)
    else:
        return declarative_base(cls=ModelBase, metadata=mymetadata)


Model = _make_sql_alchemy_base(my_engine=db)
