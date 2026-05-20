import string
import os

class Base():

    @staticmethod
    def snakeCaseToPascalCase(test_str):
        return string.capwords(test_str.replace("_", " ")).replace(" ", "")

    # removes suffix from the end of string s
    @staticmethod
    def rchop(s, suffix):
        if suffix and s.endswith(suffix):
            return s[:-len(suffix)]
        return s
    
    # removes prefix from the start of string str
    @staticmethod
    def lchop(str, prefix):
        return str.lstrip(prefix)
    
    @staticmethod
    def getVersion():
        baseDir = os.path.dirname(os.path.realpath(__file__))
        version = ''
        with open(baseDir + '/../VERSION') as f:
            version = f.readline().strip('\n')

        return version

    @staticmethod
    def parseVersion(s):
        s = (s or '').strip()
        if s.endswith('^{}'):
            s = s[:-3]
        if s.startswith('v') or s.startswith('V'):
            s = s[1:]
        parts = s.split('.')
        out = []
        for p in parts[:3]:
            try:
                out.append(int(p))
            except ValueError:
                out.append(-1)
        while len(out) < 3:
            out.append(0)
        return tuple(out)

    @staticmethod
    def compareVersions(a, b):
        pa = Base.parseVersion(a)
        pb = Base.parseVersion(b)
        if pa < pb:
            return -1
        if pa > pb:
            return 1
        return 0