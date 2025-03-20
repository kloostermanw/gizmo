import sys
import os
import glob
from importlib import import_module
from commands.command import Command
from lib.base import Base
from lib.termcolor import colored, cprint
from os.path import dirname, basename, isfile, join

def main():
    baseDir = os.path.dirname(os.path.realpath(__file__))

    # Arguments provided to gizmo.
    args = sys.argv[1:]
    list = []
    blnFound = False

    # Find commands / modules in the Commands directory.
    modules = glob.glob(join(baseDir + "/Commands", "*.py"))
    __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py') and not f.endswith('command.py')]

    # Loop though every commmand in the Commands directory.
    for mod in __all__:
        file = import_module("commands." + mod)
        myClass = getattr(file, Base.snakeCaseToPascalCase(mod))()
        strCommand = myClass.getCommand()
        list.append(myClass.getListItem())

        if (len(args) > 0 and strCommand == args[0]):
            blnFound = True
            myClass.handle(args[1:])
            break

    # If given command is not found or commando is not given show the available commands.
    if (blnFound == False):
        list = sorted(list, key=lambda x: x['command'])
        category = ''
        version = Base.getVersion()
        print('Gizmo ' + colored(version, 'green') + '\n')

        cprint('Available commands:', 'green')
        for item in list:
            
            strCommand = item["command"]
            
            if strCommand.partition(':')[0] != category:
                category = strCommand.partition(':')[0]
                print(' ' + colored(category, 'yellow'))

            strDescription = item["description"]

            print('  ' + colored(strCommand.ljust(25), 'green') + strDescription)

if __name__ == "__main__":
    main()