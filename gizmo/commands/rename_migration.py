from commands.command import Command
# pip install gitpython
import git
import os

class RenameMigration(Command):

    def configure(self):
        self.name = "celery:rename-migration";
        self.description = "renames migration files in celery web-app";
    
    def rename(self, file, oldName, newName):
        fin = open(file, "rt")
        data = fin.read()
        #replace all occurrences of the required string
        data = data.replace(oldName, newName)
        fin.close()

        fout = open(file, "wt")
        fout.write(data)
        fout.close()

    def handle(self, args):
        # Check if current directory is a git repo
        if (os.path.exists(".git") == False):
            print(".git not found.")
            exit(0)

        # Check arguments
        if(len(args) != 2):
            print('no arguments found.')
            exit(0)

        try:
            if (int(args[0]) < 1550000000):
                print('Argument 1 is not correct.')
                exit(0)

            if (int(args[0]) > 2000000000):
                print('Argument 1 is not correct.')
                exit(0)
        except ValueError:
            print('Argument 1 is not correct.')

        try:
            if (int(args[1]) < 1550000000):
                print('Argument 2 is not correct.')
                exit(0)

            if (int(args[1]) > 2000000000):
                print('Argument 2 is not correct.')
                exit(0)
        except ValueError:
            print('Argument 2 is not correct.')

        if (int(args[0]) == int(args[1])):
            print('Arguments cannot be the same.')
            exit(0)

        # className example: Migration1550000342
        className1 = 'Migration' + args[0]

        # className example: Migration1550000343
        className2 = 'Migration' + args[1]

        file1 = 'src/includes/App/Controllers/CeleryMigrations/' + className1 + '.php'              
        file2 = 'src/includes/App/Controllers/CeleryMigrations/' + className2 + '.php' 

        repo = git.Repo(search_parent_directories=True)
        branch = repo.active_branch

        if (branch.name == 'develop'):
            print('Not allowed in develop.')
            exit(0)
        
        if (branch.name == 'master'):
            print('Not allowed in master.')
            exit(0)

        if repo.untracked_files:
            print(branch.name + ' has untracked files')
            exit(0)

        if repo.is_dirty():
            print(branch.name + ' has uncommitted files')
            exit(0)

        # hash=`git log -n 1 --pretty=format:%H -- src/includes/App/Controllers/CeleryMigrations/Migration1550000343.php`
        hash = repo.git.log('-n 1', "--pretty=format:%H", "--", file2)
        if (len(hash) == 40):
            print(className2 + " is already found!, please use a different name.")
            exit(0)

        hash = repo.git.log('develop', '-n 1', "--pretty=format:%H", "--", file2)
        if (len(hash) == 40):
            print(className2 + " is already found in develop, please use a different name.")
            exit(0)

        # hash=`git log -n 2 --pretty=format:%H -- src/includes/App/Controllers/CeleryMigrations/Migration1550000342.php`
        hash = repo.git.log('-n 2', "--pretty=format:%H", "--", file1)

        if (len(hash) > 40):
            print(className1 + " occurs in several commits. This tool is unable to fix this.")
            exit(0)
        
        # Check the length of the hash
        # hash is now the commit that contains the migration file.
        if (len(hash) != 40):
            print(className1 + " is not found.")
            exit(0)
        
        # Rename filename from Migration1550000342.php to Migration1550000343.php
        repo.git.mv(file1, file2)

        # Change Classname in the file
        self.rename(file2, className1, className2)

        # Add file2 to git
        repo.index.add(file2)

        # Create Fixup commit, for the
        repo.git.commit('--fixup', hash)

        # Set rebase point 1 commit before the commit with the hash.    
        autosquash_base = hash + '~1'

        # Set editor.
        env = {'GIT_SEQUENCE_EDITOR': ':'}

        # Rebase
        repo.git.rebase(autosquash_base, interactive=True, autosquash=True, env=env, kill_after_timeout=300)
