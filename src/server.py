import subprocess
import os
from functools import reduce

def escape(args):
    result = []
    for a in args:
        if ' ' in a:
            result.append("'{}'".format(a))
        else:
            result.append(a)
    return result

class Server:
    def __init__(self, host, port, user):
        self.user = user
        self.host = host
        self.port = port

    def __host_str(self):
        return self.user + '@' + self.host

    def __port_str(self):
        if self.port == 22:
            return ''
        return ' -p '+str(self.port)

    def remote_dir(self, dir):
        return '{host}:{dir}'.format(host=self.__host_str(), dir=dir)

    def sync(self, source, dest, exclude):
        cmd = (
            'rsync -trvlH'
            ' -e "ssh{port}"'
            ' {exclude}'
            ' --delete'
            ' {src}/ {dst}').format(
                port=self.__port_str(),
                src=source,
                dst=dest,
                exclude=reduce(lambda x, y: x + ' --exclude {}'.format(y), exclude, '')
                )
        print(cmd)
        subprocess.check_call(cmd, shell=True)

    def upload(self, src, dest, exclude):
        self.mkdir(dest)
        self.sync(src, self.remote_dir(dest), exclude)

    def download(self, src, dest, exclude):
        self.sync(self.remote_dir(src), dest, exclude)

    def mkdir(self, path):
        self.cmd('mkdir -p ' + path)

    def rm(self, path):
        self.cmd('rm -rf ' + path)

    def get_command(self, cmd):
        return 'ssh -Aq{port} {host} "{cmd}"'.format(
            port=self.__port_str(), host=self.__host_str(), cmd=cmd)

    def replace_file_content(self, file, src, dest):
        self.cmd("sed -i -e 's#{src}#{dest}#' {file}".format(src=src, dest=dest, file=file))

    def getenv(self, var):
        return subprocess.check_output(self.get_command('echo \$'+var), shell=True).strip()

    def cmd(self, command):
        try:
            print(command)
            subprocess.check_call(self.get_command(command), shell=True)
        except subprocess.CalledProcessError as e:
            return e.returncode
        return 0

    def cmd_in_wd(self, wd, command):
        return self.cmd('cd {wd}; {cmd}'.format(wd=wd, cmd=command))


