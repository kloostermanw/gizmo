import os
import sys

from Commands.command import Command
from Lib.base import Base
from Lib.updater import Updater


class UpdateCheck(Command):

    def configure(self):
        self.name = "update:check"
        self.description = "Check for updates on Gizmo"
        self.config = "update"

    def handle(self, args):
        baseDir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/..')
        updater = Updater(baseDir)

        local = Base.getVersion()
        available, remote = updater.runForcedCheck()

        if remote == '' and not available:
            print('Could not reach remote — check your network connection.')
            sys.exit(1)

        if available:
            print('Update available: ' + local + ' -> ' + remote)
        else:
            print('You are up-to-date (' + local + ').')
