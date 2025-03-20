from commands.command import Command
import configparser
from subprocess import call

# pip install gitpython
import git

class Composer(Command):

    def configure(self):
        self.name = "celery:composer";
        self.description = "Runs composer command in give repo.";
        self.config = "composer";

    def handle(self, args):
        config = self.getConfig();
        default = config['DEFAULT'];
    
        list = default.get('list').split(',');
        hostname = default.get('hostname');

        if not self.checkPing(hostname):
            print(hostname + ' replies not on ping.')
            exit(0)

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
                arguments = result = ' '.join(args)
                parameters = ['-t', '-o', 'LogLevel=QUIET', hostname, "cd " + dir + "; composer " + arguments]
                output = self.runCmdRealTime('ssh', parameters);

                print(output)
        else:
            print('no repo given.')
            exit(0)
