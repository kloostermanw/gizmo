import os
import sys

from Commands.command import Command
from Lib.base import Base
from Lib.updater import Updater


class Update(Command):

    def configure(self):
        self.name = "update:now"
        self.description = "Update Gizmo"
        self.config = "update"

    def handle(self, args):
        baseDir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/..')
        updater = Updater(baseDir)

        local = Base.getVersion()
        available, remote = updater.runForcedCheck()

        if remote == '' and not available:
            print('Could not reach remote — check your network connection.')
            sys.exit(1)

        if not available:
            print('You are up-to-date (' + local + ').')
            return

        print('Updating ' + local + ' -> ' + remote)
        if not updater.runUpdate():
            sys.exit(1)
        print('Updated to ' + Base.getVersion() + '.')
