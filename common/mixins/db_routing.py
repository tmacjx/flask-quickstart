"""
sqlchemy 读写分离
https://gist.github.com/adhorn/b84dc47175259992d406
https://techspot.zzzeek.org/2012/01/11/django-style-database-routers-in-sqlalchemy/
https://jiajunhuang.com/articles/2019_12_21-autocommit.md.html
https://stackoverflow.com/questions/8947918/read-slave-read-write-master-setup/8981058#8981058
"""


from flask.ext.sqlalchemy import SQLAlchemy, get_state
import sqlalchemy.orm as orm
from functools import partial
from flask import current_app
import random


SQLALCHEMY_BINDS = {
    'master': 'mysql://foobardbdbuser:foobar123@127.0.0.1/foobardb1',
    'slave1': 'mysql://foobardbdbuser:foobar123@127.0.0.1/foobardb2',
    'slave2': ""
}


SQLALCHEMY_CLUSTER = {
    "master": "master",
    "slave": "salve1, salve2"
}

# @contextlib.contextmanager
# def get_session(rw=True):
#     s = Session() if rw else ReadOnlySession()
#     try:
#         yield s
#         s.commit()
#     except Exception:
#         s.rollback()
#         raise
#     finally:
#         s.close()


class RoutingSession(orm.Session):

    def __init__(self, db, autocommit=False, autoflush=False, **options):
        self.app = db.get_app()
        self.db = db
        self._model_changes = {}
        self.bind_key = None
        self.master_key = db.master_key
        self.slave_keys = db.slave_keys

        orm.Session.__init__(
            self, autocommit=autocommit, autoflush=autoflush,
            bind=db.engine,
            binds=db.get_binds(self.app), **options)

    def get_bind(self, mapper=None, clause=None):
        try:
            state = get_state(self.app)
        except (AssertionError, AttributeError, TypeError) as err:
            current_app.logger.info(
                "cant get configuration. default bind. Error:" + err)
            return orm.Session.get_bind(self, mapper, clause)
        """
        If there are no binds configured, connect using the default
        SQLALCHEMY_DATABASE_URI
        """
        if state is None or not self.app.config['SQLALCHEMY_BINDS']:
            if not self.app.debug:
                current_app.logger.info("Connecting -> DEFAULT")
            return orm.Session.get_bind(self, mapper, clause)

        # Writes go to the master
        elif self._flushing:  # we who are about to write, salute you
            current_app.logger.info("Connecting -> MASTER")
            self.bind_key = self.master_key
            return state.db.get_engine(self.app, bind=self.bind_key)

        # Everything else goes to the slave
        else:
            current_app.logger.info("Connecting -> SLAVE")
            slave_key = random.choice(self.slave_keys)
            self.bind_key = slave_key
            return state.db.get_engine(self.app, bind=slave_key)

    def using_bind(self, name):
        return UsingEngineContext(name, self)

    @property
    def master_bind(self):
        try:
            state = get_state(self.app)
        except (AssertionError, AttributeError, TypeError) as err:
            current_app.logger.info(
                "cant get configuration. default bind. Error:" + err)
            raise RuntimeError("cant get configuration")
        return state.db.get_engine(self.app, bind=self.master_key)

    @property
    def salve_bind(self):
        try:
            state = get_state(self.app)
        except (AssertionError, AttributeError, TypeError) as err:
            current_app.logger.info(
                "cant get configuration. default bind. Error:" + err)
            raise RuntimeError("cant get configuration")
        slave_key = random.choice(self.slave_keys)
        return state.db.get_engine(self.app, bind=slave_key)


class UsingEngineContext(object):
    def __init__(self, engine_name, session):
        self.engine_name = engine_name

        self.session = session
        self.past_engine = self.session.bind

    def __enter__(self):
        if self.engine_name == "master":
            engine = self.session.master_bind
        else:
            engine = self.session.salve_bind
        self.session.bind = engine
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.bind = self.past_engine


class RouteSQLAlchemy(SQLAlchemy):

    def init_app(self, app):
        config_binds = app.config.get("SQLALCHEMY_BINDS")
        if not config_binds:
            raise RuntimeError('Missing SQLALCHEMY_BINDS config')

        cluster = app.config['SQLALCHEMY_CLUSTER']
        if not cluster:
            raise RuntimeError('Missing SQLALCHEMY_CLUSTER config')

        self.master_keys = cluster.get("master") or []
        self.slave_keys = cluster.get("slave") or []
        super(RouteSQLAlchemy, self).init_app(app)

    def __init__(self, *args, **kwargs):
        SQLAlchemy.__init__(self, *args, **kwargs)
        self.session.using_bind = lambda s: self.session().using_bind(s)

    def create_scoped_session(self, options=None):
        if options is None:
            options = {}
        scopefunc = options.pop('scopefunc', None)
        return orm.scoped_session(
            partial(RoutingSession, self, **options), scopefunc=scopefunc
        )


db = RouteSQLAlchemy()

with db.session().using_bind("master"):
    pass


with db.session().using_bind("salve"):
    pass
