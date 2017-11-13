"""Test the 'synse.factory' Synse Server module.
"""

from synse import factory


def test_make_app():
    """Create a new instance of the Synse Server app.
    """
    app = factory.make_app()

    # check that the app we create has the expected blueprints registered
    assert 'synse.routes.core' in app.blueprints
    assert 'synse.routes.base' in app.blueprints
    assert 'synse.routes.aliases' in app.blueprints
