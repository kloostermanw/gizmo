import configparser
import os

from Commands.branches import Branches


def makeConfig(text):
    config = configparser.ConfigParser()
    config.read_string(text)
    return config


class TestHasAllFlag:
    def test_returns_true_when_all_flag_present(self):
        assert Branches().hasAllFlag(['--all']) is True

    def test_returns_false_when_no_args(self):
        assert Branches().hasAllFlag([]) is False

    def test_returns_false_for_other_args(self):
        assert Branches().hasAllFlag(['something']) is False


class TestBuildRepoMap:
    def test_empty_list_returns_empty_map(self):
        config = makeConfig("[DEFAULT]\nlist =\n")
        assert Branches().buildRepoMap(config) == {}

    def test_missing_list_returns_empty_map(self):
        config = makeConfig("[DEFAULT]\n")
        assert Branches().buildRepoMap(config) == {}

    def test_maps_names_to_paths_preserving_order(self):
        config = makeConfig(
            "[DEFAULT]\n"
            "list = web-app,web-api\n"
            "web-app = /repos/celery-web-app\n"
            "web-api = /repos/celery-web-api\n"
        )
        result = Branches().buildRepoMap(config)
        assert list(result.items()) == [
            ('web-app', '/repos/celery-web-app'),
            ('web-api', '/repos/celery-web-api'),
        ]

    def test_expands_user_home_in_paths(self):
        config = makeConfig(
            "[DEFAULT]\n"
            "list = web-app\n"
            "web-app = ~/repos/celery-web-app\n"
        )
        result = Branches().buildRepoMap(config)
        assert result['web-app'] == os.path.expanduser('~/repos/celery-web-app')

    def test_ignores_whitespace_around_names(self):
        config = makeConfig(
            "[DEFAULT]\n"
            "list = web-app , web-api\n"
            "web-app = /a\n"
            "web-api = /b\n"
        )
        result = Branches().buildRepoMap(config)
        assert list(result.keys()) == ['web-app', 'web-api']

    def test_skips_names_without_a_path(self):
        config = makeConfig(
            "[DEFAULT]\n"
            "list = web-app,ghost\n"
            "web-app = /a\n"
        )
        result = Branches().buildRepoMap(config)
        assert result == {'web-app': '/a'}
