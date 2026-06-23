from Commands.command import Command
import configparser
import os
from subprocess import call
import git

class Health(Command):

    def configure(self):
        self.name = "celery:health";
        self.description = "check the health of the current celery environment.";
        self.config = "health";

    def handle(self, args):
        config = self.getConfig();
        default = config['DEFAULT'];

        list = default.get('list').split(',');
        header = ''
        
        for r in list:
            a = self.gitCheck(r, default.get(r));
            b = self.composerCheck(r, default.get('vagrant.' + r), default.get('vagrant_dir.' + r));

            if (a != None):
                if (header != r):
                    print(r)
                    header = r
                print("  " + a)

            if (b != None):
                if (header != r):
                    print(r)
                    header = r
                print("  " + b)

        if header == '':
            print('Healty, ready to rock.')
    
    def gitCheck(self, r, dir):
        repo = git.Repo(dir, search_parent_directories=True)
        branch = repo.active_branch

        # Fetch all remotes
        for remote in repo.remotes:
            remote.fetch()

        local='develop'
        upstream='origin/develop'

        behind = repo.git.rev_list(local + '..' + upstream, count=True)

        if (behind != "0"):
            return "is " + behind + " commits behind."

    def composerCheck(self, r, boxPath, vagrantDir):
        if boxPath is None or vagrantDir is None:
            return None

        cwd = os.path.expanduser(vagrantDir)
        args = ['ssh', '-c', "cd " + boxPath + "; composer install --dry-run"]
        output = self.runCommand('vagrant', args, cwd=cwd);

        if "must be running" in output:
            return "vagrant is down, run `vagrant up`."
        if not "Nothing to install" in output:
            return "you need to run composer install."
