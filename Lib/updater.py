import configparser
import os
import sys
import time

import git

from Lib.base import Base
from Lib.termcolor import colored, cprint


class Updater:
    DEFAULT_MODE = 'reminder'
    DEFAULT_FREQUENCY_DAYS = 7

    def __init__(self, baseDir):
        self.baseDir = baseDir

    # --- paths --------------------------------------------------------------

    def _stateDir(self):
        xdg = os.environ.get('XDG_CONFIG_HOME')
        base = xdg if xdg else os.path.expanduser('~/.config')
        return os.path.join(base, 'gizmo')

    def _statePath(self):
        return os.path.join(self._stateDir(), 'state.ini')

    # --- config -------------------------------------------------------------

    def _loadConfig(self):
        config = configparser.ConfigParser()
        file1 = os.path.join(self.baseDir, 'config', 'update', 'conf.default')
        file2 = os.path.join(self.baseDir, 'config', 'update', 'conf')
        if os.path.isfile(file2):
            config.read([file1, file2])
        else:
            config.read(file1)
        return config

    def getMode(self):
        try:
            mode = self._loadConfig().get('DEFAULT', 'mode', fallback=self.DEFAULT_MODE)
        except Exception:
            mode = self.DEFAULT_MODE
        mode = (mode or '').strip().lower()
        if mode not in ('auto', 'reminder', 'prompt', 'disabled'):
            mode = self.DEFAULT_MODE
        return mode

    def getFrequencyDays(self):
        try:
            value = self._loadConfig().getint('DEFAULT', 'frequency', fallback=self.DEFAULT_FREQUENCY_DAYS)
        except Exception:
            value = self.DEFAULT_FREQUENCY_DAYS
        if value < 0:
            value = self.DEFAULT_FREQUENCY_DAYS
        return value

    def getSourceBranch(self):
        # Read [DEFAULT] source from .gitrelease; fall back to 'develop'.
        try:
            release = configparser.ConfigParser()
            release.read(os.path.join(self.baseDir, '.gitrelease'))
            return release.get('DEFAULT', 'source', fallback='develop').strip()
        except Exception:
            return 'develop'

    # --- repo helpers -------------------------------------------------------

    def _repo(self):
        return git.Repo(self.baseDir, search_parent_directories=True)

    def getOriginUrl(self):
        try:
            return self._repo().remotes.origin.url
        except Exception:
            return ''

    # --- state IO -----------------------------------------------------------

    def loadState(self):
        path = self._statePath()
        state = {'last_check': 0, 'last_known_remote_version': '', 'last_check_status': ''}
        if not os.path.isfile(path):
            return state
        try:
            cp = configparser.ConfigParser()
            cp.read(path)
            if cp.has_section('update'):
                state['last_check'] = cp.getint('update', 'last_check', fallback=0)
                state['last_known_remote_version'] = cp.get('update', 'last_known_remote_version', fallback='')
                state['last_check_status'] = cp.get('update', 'last_check_status', fallback='')
        except Exception:
            # Corrupt file: treat as empty.
            pass
        return state

    def saveState(self, state):
        os.makedirs(self._stateDir(), exist_ok=True)
        cp = configparser.ConfigParser()
        cp['update'] = {
            'last_check': str(int(state.get('last_check', 0))),
            'last_known_remote_version': str(state.get('last_known_remote_version', '')),
            'last_check_status': str(state.get('last_check_status', '')),
        }
        with open(self._statePath(), 'w') as f:
            cp.write(f)

    # --- version probe ------------------------------------------------------

    def fetchRemoteVersion(self):
        url = self.getOriginUrl()
        if not url:
            return None
        try:
            blob = git.cmd.Git().ls_remote(url, sort='-v:refname', tags=True)
        except Exception:
            return None
        if not blob:
            return ''
        first = blob.split('\n')[0]
        # Format: "<sha>\trefs/tags/<tag>" — take the tag name.
        if '\t' not in first:
            return ''
        tag = first.split('/')[-1]
        return Base.rchop(tag, '^{}')

    # --- decisions ----------------------------------------------------------

    def isCheckDue(self, state):
        last = int(state.get('last_check') or 0)
        if last <= 0:
            return True
        return (int(time.time()) - last) >= (self.getFrequencyDays() * 86400)

    def newerVersionAvailable(self, remote):
        if not remote:
            return False
        return Base.compareVersions(remote, Base.getVersion()) > 0

    # --- update action ------------------------------------------------------

    def runUpdate(self):
        try:
            repo = self._repo()
        except Exception as e:
            print('Update failed: cannot open git repo (%s).' % e)
            return False

        sourceBranch = self.getSourceBranch()
        try:
            branch = repo.active_branch.name
        except Exception as e:
            print('Update failed: cannot read active branch (%s).' % e)
            return False

        if branch != sourceBranch:
            print('Not on source branch (expected %s, got %s) — refusing to update.' % (sourceBranch, branch))
            return False

        if repo.untracked_files:
            print('Source branch has untracked files — refusing to update.')
            return False

        requirementsPath = os.path.join(self.baseDir, 'requirements.txt')
        before = self._readFile(requirementsPath)

        try:
            repo.remotes.origin.pull('--rebase')
        except Exception as e:
            print('Pull failed: %s' % e)
            return False

        after = self._readFile(requirementsPath)
        if before != after:
            cprint('requirements.txt changed — re-run ./install.sh to sync dependencies.', 'yellow')

        # Refresh state so subsequent checks see the new local version.
        state = self.loadState()
        state['last_check'] = int(time.time())
        state['last_known_remote_version'] = Base.getVersion()
        state['last_check_status'] = 'ok'
        try:
            self.saveState(state)
        except Exception:
            pass

        return True

    @staticmethod
    def _readFile(path):
        try:
            with open(path, 'rb') as f:
                return f.read()
        except Exception:
            return None

    # --- entry points -------------------------------------------------------

    def runForcedCheck(self):
        """Always probe the remote, update state, return (update_available, remote_version)."""
        remote = self.fetchRemoteVersion()
        state = self.loadState()
        now = int(time.time())
        if remote is None:
            state['last_check'] = now - max(0, (self.getFrequencyDays() - 1) * 86400) - 3600
            state['last_check_status'] = 'network_error'
            try:
                self.saveState(state)
            except Exception:
                pass
            return False, ''
        state['last_check'] = now
        state['last_known_remote_version'] = remote
        state['last_check_status'] = 'ok'
        try:
            self.saveState(state)
        except Exception:
            pass
        return self.newerVersionAvailable(remote), remote

    def maybeRunBackgroundCheck(self):
        mode = self.getMode()
        if mode == 'disabled':
            return

        state = self.loadState()
        if not self.isCheckDue(state):
            return

        remote = self.fetchRemoteVersion()
        now = int(time.time())

        if remote is None:
            # Network error: back off, retry in ~1h instead of waiting the full frequency.
            state['last_check'] = now - max(0, (self.getFrequencyDays() - 1) * 86400) - 3600
            state['last_check_status'] = 'network_error'
            try:
                self.saveState(state)
            except Exception:
                pass
            return

        state['last_check'] = now
        state['last_known_remote_version'] = remote
        state['last_check_status'] = 'ok'
        try:
            self.saveState(state)
        except Exception:
            pass

        if not self.newerVersionAvailable(remote):
            return

        local = Base.getVersion()

        if mode == 'auto':
            cprint('Gizmo update %s -> %s available. Updating now...' % (local, remote), 'yellow')
            self.runUpdate()
            return

        if mode == 'prompt' and sys.stdin.isatty():
            try:
                answer = input(colored(
                    'Gizmo update %s -> %s available. Update now? [Y/n] ' % (local, remote),
                    'yellow'
                ))
            except (EOFError, KeyboardInterrupt):
                print('')
                return
            if answer.strip().lower() in ('', 'y', 'yes'):
                self.runUpdate()
            return

        # reminder (and prompt fallback when not a TTY)
        cprint('Gizmo update %s -> %s available. Run: gizmo update:now' % (local, remote), 'yellow')
