from commands.command import Command
from lib.base import Base

# pip install gitpython
import git
import os

class Update(Command):

    def configure(self):
        self.name = "update:now";
        self.description = "Update Gizmo";

    def handle(self, args):
        blnValue = self.updatesAvailable()
        if blnValue:
            self.update()

    def update(self):
        repo = self.getRepo()
        o = repo.remotes.origin
        o.pull("--rebase")

    def updatesAvailable(self):
        repo_url = 'https://github.com/kloostermanw/gizmo.git'
        
        blob = git.cmd.Git().ls_remote(repo_url, sort='-v:refname', tags=True)
        remoteVersion = blob.split('\n')[0].split('/')[-1];
        # remove ^{} from the end
        remoteVersion = Base.rchop(remoteVersion, '^{}')

        version = Base.getVersion()
        
        if remoteVersion != version:
            print('local version ' + version + ' new version ' + remoteVersion)
            return True

        return False

    def getRepo(self):
        blnVerbose = False
        sourceBranch = 'develop'

        if (os.path.exists(".git") == False):
            print(".git not found.")
            exit(0)

        repo = git.Repo(search_parent_directories=True)
        branch = repo.active_branch

        if branch.name == sourceBranch:
            if blnVerbose:
                print(branch.name)
        else:
            print('no ' + sourceBranch + ' branch found' +  ' but ' + branch.name)
            exit(0)

        if repo.untracked_files:
            print(sourceBranch + ' branch has untracked files')
            exit(0)

        # if repo.is_dirty():
        #     print(sourceBranch + ' branch has uncommitted files')
        #     exit(0)
        
        return repo