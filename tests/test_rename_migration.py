import subprocess

import git

from Commands.rename_migration import RenameMigration


def run(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def makeRepoWithIndexVersion3(tmp_path):
    run(tmp_path, 'init')
    (tmp_path / 'live').write_text('x')
    run(tmp_path, 'add', 'live')
    run(tmp_path, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-m', 'init')
    # skip-worktree sets an extended flag, which makes git write index version 3
    run(tmp_path, 'update-index', '--skip-worktree', 'live')
    with open(tmp_path / '.git' / 'index', 'rb') as f:
        assert f.read(8)[4:] == b'\x00\x00\x00\x03'
    return git.Repo(tmp_path)


class TestStageFile:
    def test_stages_file_when_index_is_version_3(self, tmp_path):
        repo = makeRepoWithIndexVersion3(tmp_path)
        (tmp_path / 'Migration1550000667.php').write_text('<?php')

        RenameMigration().stageFile(repo, 'Migration1550000667.php')

        assert run(tmp_path, 'diff', '--cached', '--name-only').split() == ['Migration1550000667.php']
