#!/usr/bin/python
# -*- coding:utf8 -*-
import os
import ftplib
import re
import sys
import argparse


def ftp_config():
    """
    --FTP Config Manager--
    """
    config = {
        "server": (
            {"host_name": "ftp-a",
             "host": "127.0.0.1",
             "user": "",
             "pwd": "",
             "server_base_dir": "home"},
            {"host_name": "ftp_2",
             "host": "127.0.0.1",
             "user": "",
             "pwd": "",
             "server_base_dir": "app"}
        ),
        "local_dir": "/home/localhost/",
        "execute_thread": 1

    }
    return config


def local_dir_init():
    """
    --Local FTP  Directories For DownLoad--
    """
    local_dir = "%s/%s" % (ftp_config()["local_dir"], raw_input("input your directory to download file:"))
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    return local_dir


def ftp_connection(func):
    """
    --FTP Connection Manager (Manage the open/quit connection of ftp)--
    """
    def _ftp_connection(server, *params):
        print "login in server:%s" % (server["host"])
        ftp = ftplib.FTP(server["host"], server["user"], server["pwd"])
        result = func(ftp, server, *params)
        print "login out server:%s" % (server["host"])
        ftp.close()
        return result

    return _ftp_connection


@ftp_connection
def file_list(ftp, server, re_dir, re_file, extra_dir):
    """
    --FTP File List Manager (list the file to download, /server_base_dir/re_dir/extra_dir/re_file)--
    """
    ftp.cwd("/%s/" % (server["server_base_dir"], ))

    dir_match = []
    for temp_dir in ftp.nlst():
        if re.search(re_dir, temp_dir):
            dir_match.append(temp_dir)

    file_match = []
    for dir_hand in dir_match:
        to_dir = "/%s/%s/%s/" % (server["server_base_dir"], dir_hand, extra_dir)
        try:
            ftp.cwd(to_dir)
        except ftplib.error_perm:
            continue

        for temp_file in ftp.nlst():
            if re.search(re_file, temp_file):
                file_match.append((to_dir, temp_file))
                print "Found file: %s%s" % (to_dir, temp_file)

    if not file_match:
        return

    is_confirm = raw_input("[confirm] are you sure download above files(y/n)?")
    if not ("y" == is_confirm or "Y" == is_confirm):
        return
    return file_match


@ftp_connection
def file_download(ftp, server, file_download_list, download_dir):
    """
    --FTP File Download Manager (download file of file_download_list)--
    """
    if not file_download_list:
        print "skip download, no file found."
        return

    os.chdir(download_dir)

    for _file in file_download_list:
        file_dir = _file[0]
        file_name = _file[1]
        ftp.cwd(file_dir)
        down_name = "%s-%s" % (server["host_name"], file_name)
        ftp.retrbinary('RETR %s' % file_name, open(down_name, 'wb').write)
        print('Download Success: %s -> %s ' % (_file, down_name))


def batch_download_manager(opts):

    _re_dir = str(opts.re_dir)
    _re_file = str(opts.re_file)
    _extra_dir = str(opts.extra_dir)

    _download_dir = local_dir_init()
    print ("download to directory: %s" % (_download_dir,))

    servers = ftp_config()["server"]
    for _server in servers:
        _file_download_list = file_list(_server, _re_dir, _re_file, _extra_dir)
        file_download(_server, _file_download_list, _download_dir)

if __name__ == '__main__':
    """
    USAGE: python ftp_batch.py --re_dir tomcat --re_file log, --extra_dir logs
    """
    reload(sys)
    sys.setdefaultencoding('utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--re_dir', help='下载路径名')
    parser.add_argument('--re_file', help='下载文件名')
    parser.add_argument('--extra_dir', help='下载文件名')
    batch_download_manager(parser.parse_args())

