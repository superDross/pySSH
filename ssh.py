#!/usr/bin/python3
''' Send and execute a command or script to a remote host.'''
import argparse
import getpass
import paramiko


class SSH(object):
    ''' Connection to a remote host.

    Attributes:
        hostname (str): name of host to connect to.
        username (str): name of user to connect to host as.
        key (str): path to ssh key.
        port (int): host port to connect to.
    '''

    def __init__(self, hostname, username, key, port=22):
        self.hostname = hostname
        self.username = username
        self.key = key
        self.port = port
        self.sshcon = None

    def execute(self, commands):
        ''' Connect to host and execute the given command.

        Args:
            commands (str | list): semicolon seperated bash commands.
        '''
        self._connect()
        self._execute_commands(commands)

    def transfer_and_execute(self, script, destination, delete=False):
        ''' Transfer a script and execute it on host.

        Args:
            script (str): local script path to transfer to host.
            destination (str): where to copy the script on host.
            delte (bool): whether to delete the script after usage.
        '''
        self._connect()
        self.transfer(script, destination)
        command = 'chmod +x ' + destination + ';' + destination
        if delete:
            command += '; rm ' + destination
        self._execute_commands(command)

    def _connect(self):
        ''' Connect to host.'''
        print('connecting to ' + self.hostname + '\n' + '-'*20)
        self.sshcon = paramiko.SSHClient()
        self.sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.sshcon.connect(self.hostname, username=self.username,
                                key_filename=self.key, port=self.port)
        except paramiko.ssh_exception.NoValidConnectionsError:
            print('Failed to connect using keys')
            password = getpass.getpass()
            self.sshcon.connect(self.hostname, username=self.username,
                                password=password, port=self.port)

    def transfer(self, script, destination):
        ''' Transfer a file from local to host.

        Args:
            script (str): local script path to transfer to host.
            destination (str): where to copy the script on host.
        '''
        print('Transferring '+script + ' to ' + destination)
        sftp = self.sshcon.open_sftp()
        try:
            sftp.put(script, destination)
        except OSError:
            raise OSError(destination +
                          ' is a directory but must be a path to a file')

    def _execute_commands(self, commands):
        ''' Execute commands on host.

        Args:
            commands (str|list): semicolon seperated bash commands.
        '''
        if isinstance(commands, list):
            commands = ' '.join(commands)
        stdin, stdout, stderr = self.sshcon.exec_command(commands)
        stdout, stderr = stdout.read(), stderr.read()
        if stdout:
            print(stdout.decode(encoding='utf-8'))
        else:
            print(stderr.decode(encoding='utf-8'))
        self.sshcon.close()


def get_parser():
    parser = argparse.ArgumentParser(description='automates ssh tasks')
    parser.add_argument('-n', '--hostnames', nargs='*', required=True,
                        help='hosts to execute commands upon')
    parser.add_argument('-u', '--username', required=True,
                        help='username to log into host(s)')
    parser.add_argument('-p', '--port', default=22,
                        help='host port to conect to')
    parser.add_argument('-k', '--key', help='key to access host(s)')
    parser.add_argument('-c', '--commands', nargs='*',
                        help='commands to execute on host (semicolon seperated)')
    parser.add_argument('-s', '--script', help='script to execute on host(s)')
    parser.add_argument('-d', '--destination', help='where to scp the script.')
    parser.add_argument('--delete', action='store_true',
                        help='delete the scripta fter execution')
    return parser


def cli():
    # retrieve all args
    parser = get_parser()
    args = vars(parser.parse_args())
    # argument error handeling
    if args['commands'] and args['script']:
        raise ValueError('Parse either --command or --script arg, not both.')
    if args['script'] and not args['destination']:
        raise ValueError('--script requires --destination arg to be set')
    # connect to all hosts and execute the commands/script
    for hostname in args['hostnames']:
        ssh = SSH(hostname, args['username'], args['key'], args['port'])
        if args['commands']:
            ssh.execute(args['commands'])
        elif args['script']:
            ssh.transfer_and_execute(
                args['script'], args['destination'], args['delete'])


if __name__ == '__main__':
    cli()
