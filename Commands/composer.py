from Commands.command import Command
import configparser
from subprocess import call

# pip install gitpython
import git

class Composer(Command):

    def configure(self):
        self.name = "celery:composer";
        self.description = "Run composer command";
        self.config = "composer";

    def handle(self, args):
        config = self.getConfig();
        default = config['DEFAULT'];
    
        list = default.get('list').split(',');

        # Extract --repo value
        repo = next((item.split('=')[1] for item in args if item.startswith('--repo=')), None);   
        
        # Remove all items starting with '--repo'
        args = [item for item in args if not item.startswith('--repo')];

        if repo in list:
            if(len(args) == 0):
                print('no arguments given for composer.')
                exit(0)

            dir = default.get(repo);
        
            if dir != None:
                hostname = 'pg.celery.loc'
                arguments = result = ' '.join(args)
                parameters = ['-t', '-o', 'LogLevel=QUIET', hostname, "cd " + dir + "; composer " + arguments]
                output = self.runCmdRealTime('ssh', parameters);

                print(output)
        else:
            print('no repo given.')
            exit(0)
