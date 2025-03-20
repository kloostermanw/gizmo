from commands.update import Update

# pip install gitpython
import git

class UpdateCheck(Update):

    def configure(self):
        self.name = "update:check";
        self.description = "Check for updates on Gizmo";

    def handle(self, args):
        blnValue = self.updatesAvailable()
        if blnValue:
            print("update available!")
        else:
            print("You are up-to-date.")
