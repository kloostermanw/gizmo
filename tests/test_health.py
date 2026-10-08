import subprocess

from Commands.health import Health


def git(cwd, *args):
    subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True)


def makeRepoWithOrigin(tmp_path):
    origin = tmp_path / 'origin.git'
    repo = tmp_path / 'repo'
    git(tmp_path, 'init', '--bare', '-b', 'develop', str(origin))
    git(tmp_path, 'clone', str(origin), str(repo))
    git(repo, 'checkout', '-b', 'develop')
    git(repo, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '--allow-empty', '-m', 'init')
    git(repo, 'push', 'origin', 'develop')
    return repo


class TestGitCheck:
    def test_reports_missing_directory(self, tmp_path):
        missing = tmp_path / 'does-not-exist'
        result = Health().gitCheck('dev3', str(missing))
        assert result == 'directory ' + str(missing) + ' not found.'

    def test_reports_directory_that_is_not_a_git_repo(self, tmp_path):
        result = Health().gitCheck('dev3', str(tmp_path))
        assert result == 'directory ' + str(tmp_path) + ' is not a git repository.'

    def test_returns_none_when_up_to_date(self, tmp_path):
        repo = makeRepoWithOrigin(tmp_path)
        assert Health().gitCheck('web-app', str(repo)) is None


class TestComposerCheck:
    def test_returns_none_when_not_configured(self):
        assert Health().composerCheck('devops', None, None) is None

    def test_reports_missing_vagrant_directory(self, tmp_path):
        missing = tmp_path / 'does-not-exist'
        result = Health().composerCheck('dev3', '/var/www/vhosts/application/src', str(missing))
        assert result == 'vagrant directory ' + str(missing) + ' not found.'
