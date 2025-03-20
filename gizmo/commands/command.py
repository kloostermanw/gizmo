import configparser
import subprocess
import os.path
from subprocess import run
from subprocess import PIPE, STDOUT
from subprocess import Popen

class Command:
    def __init__(self):
        self.configure()
    
    def configure(self):
        self.name = "";
        self.description = "";
        self.config = "";

    def getCommand(self):
        return self.name
    
    def getDescription(self):
        return self.description
    
    def getListItem(self):
        return {
            "command": self.name,
            "description": self.description
        }
    
    def getConfig(self):
        config = configparser.ConfigParser();
        config.sections();
        
        baseDir = os.path.dirname(os.path.realpath(__file__));
        
        file1 = baseDir + '/../config/' + self.config + '/conf.default';
        file2 = baseDir + '/../config/' + self.config + '/conf';

        if (not os.path.isfile(file1)):
            print('config does not exist ', file1)

        if (os.path.isfile(file2)):
            config.read([file1, file2])
        else:
            config.read(file1);

        return config;

    def runCommand(self, strCmd, strArgs):
        arrCmdAndArgs = []
        
        if type(strArgs) is list:
            arrCmdAndArgs = strArgs
        else:
            if strArgs != 'none':
                arrCmdAndArgs = strArgs.split()

        arrCmdAndArgs.insert(0, strCmd)
        if strCmd != 'none':
            result = run(arrCmdAndArgs,
                            shell=False,
                            stdout=PIPE,
                            stderr=PIPE,
                            check=False)

            return result.stderr.decode("utf-8")

    # To ensure the command outputs real-time to the terminal exactly as if you ran it manually
    def runCmdRealTime(self, strCmd, strArgs):
        arrCmdAndArgs = []
        
        if type(strArgs) is list:
            arrCmdAndArgs = strArgs
        else:
            if strArgs != 'none':
                arrCmdAndArgs = strArgs.split()

        arrCmdAndArgs.insert(0, strCmd)
        if strCmd != 'none':
            process = subprocess.Popen(arrCmdAndArgs, shell=False)
            process.communicate()

    def checkPing(self, hostname):
        response = os.system("ping -c 1 " + hostname)
        
        return response == 0