"""
"""
import unittest

import click
import coverage as cover
from flask import current_app
from flask.cli import FlaskGroup
from flask_migrate import MigrateCommand
from pylint import epylint as lint

from app import config
from app import create_app, __version__
from app.cli import database


def create(group):
    app = current_app or create_app(config)
    group.app = app

    @app.shell_context_processor
    def shell_context():
        from app import models
        return dict(models=models)

    return app


@click.group(cls=FlaskGroup, create_app=create)
def manager():
    """Management script for app"""


manager.add_command('db', MigrateCommand)
manager.add_command(database.manager, "database")

COV = cover.coverage(
    branch=True,
    include='app/*',
    omit=[
        'app/tests/*',
        'app/config/*',
    ]
)


@manager.command()
def version():
    """Displays app version."""
    print(__version__)


# todo 输出当前配置
# @manager.command()
# def check_settings():
#     """Show the settings as Redash sees them (useful for debugging)."""
#     for name, item in settings.all_settings().iteritems():
#         print("{} = {}".format(name, item))


lint_options = "app"


@manager.command()
def pep8():
    """Run the Pylint"""
    lint.py_run(lint_options)


@manager.command()
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('app/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command()
def coverage():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('app/tests')
    COV.start()
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


@manager.command()
def ipython():
    """Starts IPython shell instead of the default Python shell."""
    import sys
    import IPython
    from flask.globals import _app_ctx_stack
    app = _app_ctx_stack.top.app

    banner = 'Python %s on %s\nIPython: %s\nRedash version: %s\n' % (
        sys.version,
        sys.platform,
        IPython.__version__,
        __version__
    )

    ctx = {}
    ctx.update(app.make_shell_context())

    IPython.embed(banner1=banner, user_ns=ctx)


# @manager.command
# def runserver():
#     """Run the application with DEBUG"""
#     # 127.0.0.1:5000
#     run(debug=True)


# if __name__ == '__main__':
#     manager.run()
