"""Test the 'synse.config' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import copy
import os
import shutil

import pytest
import yaml

from synse import config


@pytest.fixture()
def json_config():
    """Create a JSON file for configuration."""
    if not os.path.isdir('_tmp'):
        os.mkdir('_tmp')

    cfg_file = '_tmp/config.json'
    with open(cfg_file, 'w') as f:
        f.write('{}')

    yield cfg_file

    if os.path.isdir('_tmp'):
        shutil.rmtree('_tmp')


@pytest.fixture()
def clear_config():
    """Reset options to an empty dictionary"""
    yield
    config.options = {}


@pytest.fixture()
def clear_environ():
    """Remove test data put in environment variables."""
    yield
    for k, _ in os.environ.items():
        if k.startswith('SYNSE_'):
            del os.environ[k]


@pytest.fixture()
def set_test_config():
    """Fixture to set a test configuration YAML"""
    config = {
        'pretty_json': True,
        'logging': 'debug'
    }

    if not os.path.isdir('_tmp'):
        os.mkdir('_tmp')

    cfg_file = '_tmp/config.yml'
    with open(cfg_file, 'w') as f:
        yaml.dump(config, f)

    _old_env = os.environ.get('SYNSE_CONFIG')
    os.environ['SYNSE_CONFIG'] = cfg_file

    yield

    if _old_env:
        os.environ['SYNSE_CONFIG'] = _old_env
    else:
        del os.environ['SYNSE_CONFIG']

    shutil.rmtree('_tmp')


def test_load_default_configs(clear_config):
    """Load defaults configurations"""
    assert len(config.options) == 0

    expected_defaults = {
        'locale': 'en_US',
        'pretty_json': False,
        'logging': 'info',
        'cache': {
            'meta': {
                'ttl': 20
            },
            'transaction': {
                'ttl': 20
            }
        },
        'grpc': {
            'timeout': 3
        }
    }

    config.load_default_configs()
    assert len(config.options) != 0
    assert config.options == expected_defaults


def test_parse_user_configs_no_file():
    """Parse user configurations using a wrong default configuration filepath"""
    config.DEFAULT_CONFIG_PATH = '/synse/config/nothing.yml'
    cfg_start = copy.deepcopy(config.options)
    config.parse_user_configs()
    assert cfg_start == config.options


def test_parse_user_configs_unsupported_ext(json_config):
    """Parse user configurations using an unsupported file extension"""
    config.DEFAULT_CONFIG_PATH = json_config
    with pytest.raises(ValueError):
        config.parse_user_configs()


def test_parse_user_configs_default_path_yml_ext(set_test_config, clear_config):
    """Parse user configurations using a .yml default configuration file path"""
    assert len(config.options) == 0

    config.options = {
        'pretty_json': False,
        'logging': 'info',
    }

    assert config.options.get('pretty_json') is False
    assert config.options.get('logging') == 'info'

    config.parse_user_configs()

    assert len(config.options) != 0
    # these values are set via the `set_test_config` fixture
    assert config.options.get('pretty_json') is True
    assert config.options.get('logging') == 'debug'


def test_parse_user_configs_default_path_yaml_ext(tmpdir, clear_config):
    """Parse user configurations using a .yml default configuration file path"""
    assert len(config.options) == 0

    config.options = {
        'pretty_json': False,
    }

    assert config.options.get('pretty_json') is False

    path = tmpdir.mkdir('tmp').join('test.yaml')
    path.write('pretty_json: True')

    config.DEFAULT_CONFIG_PATH = str(path)
    config.parse_user_configs()

    expected_configs = {
        'pretty_json': True,
    }

    assert len(config.options) != 0
    assert config.options == expected_configs


def test_parse_user_configs_custom_path_yml_ext(tmpdir, clear_environ, clear_config):
    """Parse user configurations using a .yml custom configuration file path"""
    assert len(config.options) == 0

    config.options = {
        'foo': 'bar'
    }

    assert config.options.get('foo') == 'bar'

    path = tmpdir.mkdir('tmp').join('test.yml')
    path.write('foo: foobar')

    os.environ['SYNSE_CONFIG'] = str(path)
    config.parse_user_configs()
    assert config.options.get('foo') == 'foobar'


def test_parse_user_configs_custom_path_yaml_ext(tmpdir, clear_environ, clear_config):
    """Parse user configurations using a .yaml custom configuration file path"""
    assert len(config.options) == 0

    config.options = {
        'foo': 'bar'
    }

    assert config.options.get('foo') == 'bar'

    path = tmpdir.mkdir('tmp').join('test.yaml')
    path.write('foo: foobar')

    os.environ['SYNSE_CONFIG'] = str(path)
    config.parse_user_configs()
    assert config.options.get('foo') == 'foobar'


def test_parse_env_vars_str(clear_environ, clear_config):
    """Parse a string-type environment variable"""
    assert len(config.options) == 0

    config.options['foo'] = 'bar'
    assert config.options.get('foo') == 'bar'

    os.environ['SYNSE_FOO'] = 'foobar'
    config.parse_env_vars()
    assert config.options.get('foo') == 'foobar'


def test_parse_env_vars_int(clear_environ, clear_config):
    """Parse an integer-type environment variable"""
    assert len(config.options) == 0

    config.options = {
        'grpc': {
            'timeout': 10
        },
        'cache': {
            'meta': {
                'ttl': 10
            }
        }
    }

    assert config.options.get('grpc').get('timeout') == 10
    assert config.options.get('cache').get('meta').get('ttl') == 10

    os.environ['SYNSE_GRPC_TIMEOUT'] = '101'
    os.environ['SYNSE_CACHE_META_TTL'] = '101'
    config.parse_env_vars()
    assert config.options.get('grpc').get('timeout') == 101
    assert config.options.get('cache').get('meta').get('ttl') == 101


def test_parse_env_vars_bool(clear_environ, clear_config):
    """Parse a boolean-type environment variable"""
    assert len(config.options) == 0

    config.options['foo'] = False
    assert config.options.get('foo') is False

    os.environ['SYNSE_FOO'] = 'True'
    config.parse_env_vars()
    assert config.options.get('foo') is True

    os.environ['SYNSE_FOO'] = 'False'
    config.parse_env_vars()
    assert config.options.get('foo') is False


def test_parse_env_vars_nested(clear_environ, clear_config):
    """Parse an environment variable using a nested key"""
    assert len(config.options) == 0

    config.options = {
        'one': {
            'two': {
                'three': 'foo'
            }
        }
    }

    assert config.options.get('one').get('two').get('three') == 'foo'

    os.environ['SYNSE_ONE_TWO_THREE'] = 'bar'
    config.parse_env_vars()
    assert config.options.get('one').get('two').get('three') == 'bar'


def test_parse_env_vars_config_file(tmpdir, clear_environ, clear_config):
    """Parse an environment variable with a configuration file path"""
    assert len(config.options) == 0

    config.options = {
        'foo': 'bar'
    }

    assert config.options.get('foo') == 'bar'

    path = tmpdir.mkdir('tmp').join('test.yaml')
    path.write('foo: foobar')

    os.environ['SYNSE_CONFIG'] = str(path)
    assert config.options.get('foo') == 'bar'

    config.parse_user_configs()
    config.parse_env_vars()
    assert config.options.get('foo') == 'foobar'


def test_load_no_env(clear_environ, clear_config):
    """Load all configurations without setting any environment variable"""
    assert len(config.options) == 0

    config.load()
    assert len(config.options) != 0


def test_load_env(clear_environ, clear_config):
    """Load allconfigurations while setting a test environment variable"""
    assert len(config.options) == 0

    config.options['foo'] = 'bar'
    assert config.options.get('foo') == 'bar'

    os.environ['SYNSE_FOO'] = 'foobar'
    config.load()
    assert config.options.get('foo') == 'foobar'


def test_merge_dicts_none_type_error():
    """Merge non-type dictionaries"""
    temp = {
        'foo': 'bar'
    }

    with pytest.raises(AttributeError):
        config.merge_dicts(temp, None)

    with pytest.raises(TypeError):
        config.merge_dicts(None, temp)


def test_merge_dicts_empty():
    """Merge empty dictionaries"""
    temp = {
        'foo': 'bar'
    }

    config.merge_dicts(temp, {})
    assert temp == {'foo': 'bar'}


def test_merge_dicts_normal_add():
    """Merge two normal/non-nested dictionaries. Add a new value"""
    temp_foo = {
        'foo': 'foo'
    }

    temp_bar = {
        'bar': 'bar'
    }

    temp_foobar = {
        'foo': 'foo',
        'bar': 'bar'
    }

    config.merge_dicts(temp_foo, temp_bar)
    assert temp_foo == temp_foobar


def test_merge_dicts_normal_overwrite():
    """Merge two normal/non-nested dictionaries. Overwrite an existing value"""
    temp_foo = {
        'foo': 'foo'
    }

    temp_new_foo = {
        'foo': 'new_foo'
    }

    config.merge_dicts(temp_foo, temp_new_foo)
    assert temp_foo.get('foo') == 'new_foo'


def test_merge_dicts_nested_add():
    """Merge nested dictionaries. Add a new value"""
    temp_foo = {
        'one': {
            'two': {
                'three': 'foo'
            }
        }
    }

    temp_bar = {
        'one': {
            'two': {
                'four': 'bar'
            }
        }
    }

    config.merge_dicts(temp_foo, temp_bar)
    assert temp_foo.get('one').get('two').get('three') == 'foo'
    assert temp_foo.get('one').get('two').get('four') == 'bar'


def test_merge_dicts_nested_overwrite():
    """Merge nested dictionaries. Overwrite an existing value"""
    temp_foo = {
        'one': {
            'two': {
                'three': 'foo'
            }
        }
    }

    temp_bar = {
        'one': {
            'two': {
                'three': 'bar'
            }
        }
    }

    config.merge_dicts(temp_foo, temp_bar)
    assert temp_foo.get('one').get('two').get('three') == 'bar'


def test_set_value_type_str():
    """Set the right value for a string"""
    assert config.set_value_type('foo', 'bar') == 'bar'


def test_set_value_type_int():
    """Set the right value for an integer"""
    assert config.set_value_type('grpc', '10') == 10
    assert config.set_value_type('cache', '10') == 10


def test_set_normal(clear_config):
    """Set a value for a normal/non-nested key"""
    assert len(config.options) == 0

    config.options['foo'] = 'bar'
    assert config.options.get('foo') == 'bar'

    config.update_options('foo', 'foo')
    assert config.options.get('foo') == 'foo'


def test_set_nested_key(clear_config):
    """Set a value for a nested key"""
    assert len(config.options) == 0

    config.options = {
        'one': {
            'two': {
                'three': 'foo'
            }
        }
    }

    assert config.options.get('one').get('two').get('three') == 'foo'

    config.update_options('one.two.three', 'bar')
    assert config.options.get('one').get('two').get('three') == 'bar'
