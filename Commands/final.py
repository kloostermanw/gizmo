from Commands.command import Command
from Lib.termcolor import colored, cprint
import subprocess
import shutil
import time
import sys
import os


SPINNER = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']


class Final(Command):

    def configure(self):
        self.name = "final"
        self.description = "run all final checks in parallel (configurable in config/final/conf)."
        self.config = "final"

    def handle(self, args):
        # Find git root from current working directory
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            git_root = result.stdout.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            print(colored('Error: not inside a git repository', 'red'))
            return

        work_dir = os.path.join(git_root, 'src')

        if not os.path.isdir(work_dir):
            print(colored('Error: ' + work_dir + ' does not exist', 'red'))
            return

        # Load configured commands
        config = self.getConfig()
        default = config['DEFAULT']

        command_keys = default.get('list').split(',')

        # Start all processes in parallel
        processes = {}
        order = []
        for key in command_keys:
            key = key.strip()
            cmd_str = default.get(key)

            if cmd_str is None:
                print(colored('Warning: no command configured for "' + key + '", skipping.', 'yellow'))
                continue

            cmd_parts = cmd_str.strip().split()

            try:
                proc = subprocess.Popen(
                    cmd_parts,
                    cwd=work_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                processes[key] = {
                    'process': proc,
                    'command': cmd_str,
                    'start_time': time.time(),
                }
                order.append(key)
            except Exception as e:
                print(colored('Failed to start "' + key + '": ' + str(e), 'red'))

        if not processes:
            print(colored('No commands to run.', 'yellow'))
            return

        total = len(processes)
        completed = {}

        print(colored('Running ' + str(total) + ' commands in parallel from ' + work_dir, 'cyan'))
        print()

        spin_index = 0
        term_width = shutil.get_terminal_size().columns

        # Main loop: single-line spinner, permanent result lines above
        while len(completed) < total:
            # Check for newly finished processes
            newly_done = []
            for key in order:
                if key in completed:
                    continue

                info = processes[key]
                retcode = info['process'].poll()
                if retcode is not None:
                    elapsed = time.time() - info['start_time']
                    output = info['process'].stdout.read()
                    completed[key] = {
                        'returncode': retcode,
                        'elapsed': elapsed,
                        'output': output,
                    }
                    newly_done.append(key)

            # If something finished, clear the spinner line and print results
            if newly_done:
                # Overwrite spinner line with blanks
                sys.stdout.write('\r' + ' ' * term_width + '\r')
                for key in newly_done:
                    res = completed[key]
                    sys.stdout.write(self.format_result(key, res) + '\n')
                    if res['returncode'] != 0 and res['output'].strip():
                        for out_line in res['output'].strip().split('\n'):
                            sys.stdout.write('         ' + out_line + '\n')

            # Show single-line spinner with all running commands
            running = [k for k in order if k not in completed]
            if running:
                spinner_char = colored(SPINNER[spin_index % len(SPINNER)], 'yellow')
                parts = []
                for key in running:
                    elapsed = time.time() - processes[key]['start_time']
                    parts.append(
                        colored(key, 'cyan') + ' ' + self.format_time(elapsed)
                    )
                line = '  ' + spinner_char + '  ' + colored(' | ', 'white').join(parts)
                # Pad to terminal width to clear previous content, then \r back
                sys.stdout.write('\r' + line + ' ' * 10 + '\r')

            sys.stdout.flush()
            spin_index += 1

            if len(completed) < total:
                time.sleep(0.1)

        # Clear spinner line
        sys.stdout.write('\r' + ' ' * term_width + '\r')
        sys.stdout.flush()

        # Final summary
        print()
        self.print_summary(completed)

    def format_result(self, key, result):
        elapsed_str = self.format_time(result['elapsed'])

        if result['returncode'] == 0:
            status = colored('PASS', 'green')
        else:
            status = colored('FAIL', 'red')

        return '  ' + status + '  ' + colored(key.ljust(15), 'cyan') + elapsed_str

    def print_summary(self, completed):
        passed = sum(1 for r in completed.values() if r['returncode'] == 0)
        failed = sum(1 for r in completed.values() if r['returncode'] != 0)
        total = len(completed)

        if failed == 0:
            cprint('All ' + str(total) + ' checks passed.', 'green')
        else:
            print(colored(str(passed) + '/' + str(total) + ' passed', 'green')
                  + ', '
                  + colored(str(failed) + ' failed', 'red'))

    def format_time(self, seconds):
        if seconds < 60:
            return str(round(seconds, 1)) + 's'
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return str(minutes) + 'm ' + str(secs) + 's'
