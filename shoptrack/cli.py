import click
from flask.cli import with_appcontext
from .database import engine, Base

@click.command()
@with_appcontext
def init_db():
    """Clear the existing data and create new tables."""
    Base.metadata.create_all(bind=engine)
    click.echo('Initialized the database.')

@click.command()
@with_appcontext
def reset_db():
    """Drop all tables and create new ones."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    click.echo('Reset the database.')