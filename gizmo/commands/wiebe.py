from commands.command import Command

class Wiebe(Command):

    def configure(self):
        self.name = "local:wiebe";
        self.description = "wiebes test command";

    def handle(self, args):
        print('main')
        print(args)
