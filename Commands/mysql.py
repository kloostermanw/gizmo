from Commands.command import Command
import os
import shlex
import subprocess


class Mysql(Command):

    def configure(self):
        self.name = "mysql"
        self.description = "Run a MySQL query against a configured profile (direct or over SSH)."
        self.config = "mysql"

    def handle(self, args):
        if len(args) < 2:
            print('Usage: gizmo mysql <profile> "<query>"')
            return

        profile = args[0]
        query = ' '.join(args[1:])

        config = self.getConfig()

        if profile not in config.sections():
            print('Profile not found: ' + profile)
            available = config.sections()
            if available:
                print('Available profiles: ' + ', '.join(available))
            return

        section = config[profile]

        mysql_host = section.get('mysql.host', '127.0.0.1')
        mysql_port = section.get('mysql.port', '3306')
        mysql_user = section.get('mysql.user', '')
        mysql_password = self.resolvePassword(section.get('mysql.password', ''))
        if mysql_password is None:
            return
        mysql_database = section.get('mysql.database', '')

        ssh_server = section.get('ssh.server', '').strip()

        if ssh_server:
            self.runOverSsh(section, ssh_server, mysql_host, mysql_port, mysql_user, mysql_password, mysql_database, query)
        else:
            self.runDirect(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database, query)

    def runDirect(self, host, port, user, password, database, query):
        cmd = ['mysql', '-h', host, '-P', port]
        if user:
            cmd += ['-u', user]
        if database:
            cmd.append(database)

        env = os.environ.copy()
        if password:
            env['MYSQL_PWD'] = password

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, env=env)
        proc.communicate(input=query.encode())

    def runOverSsh(self, section, server, host, port, user, password, database, query):
        ssh_port = section.get('ssh.port', '').strip()
        ssh_key = section.get('ssh.key', '').strip()
        ssh_user = section.get('ssh.user', '').strip()

        ssh_cmd = ['ssh']
        if ssh_port:
            ssh_cmd += ['-p', ssh_port]
        if ssh_key:
            key_path = ssh_key if os.path.isabs(ssh_key) else os.path.expanduser('~/.ssh/' + ssh_key)
            ssh_cmd += ['-i', key_path]

        target = (ssh_user + '@' + server) if ssh_user else server

        remote_parts = ['mysql', '-h', host, '-P', port]
        if user:
            remote_parts += ['-u', user]
        if database:
            remote_parts.append(database)

        remote_cmd = ' '.join(shlex.quote(p) for p in remote_parts)
        if password:
            # MYSQL_PWD avoids -p showing the password in the remote process list.
            remote_cmd = 'MYSQL_PWD=' + shlex.quote(password) + ' ' + remote_cmd

        ssh_cmd += [target, remote_cmd]

        proc = subprocess.Popen(ssh_cmd, stdin=subprocess.PIPE)
        proc.communicate(input=query.encode())

    def resolvePassword(self, password):
        # Treat values like "op://vault/item/field" as 1Password secret references
        # and resolve them via the `op` CLI. Returns None on failure so the caller
        # can abort without leaking a placeholder value.
        password = password.strip().strip('"').strip("'")
        if not password.startswith('op://'):
            return password

        try:
            result = subprocess.run(
                ['op', 'read', password],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except FileNotFoundError:
            print('1Password CLI (op) not found but a 1Password reference is configured.')
            return None

        if result.returncode != 0:
            err = result.stderr.decode('utf-8').strip()
            print('Failed to resolve 1Password reference: ' + (err or password))
            return None

        return result.stdout.decode('utf-8').rstrip('\n')
