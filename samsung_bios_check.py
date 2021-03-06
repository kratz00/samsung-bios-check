#!/usr/bin/env python

# This file is sourced from the project https://github.com/damianmoore/samsung-bios-check
# Copyright (C) 2013 Damian Moore
# For licencing please refer to the the project LICENSE file

from re import findall
from subprocess import Popen, PIPE
from time import sleep
try:
    from urllib import urlopen
except:
    from urllib.request import urlopen


def run_command(cmd):
    p = Popen(cmd.split(' '), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return p.communicate()[0].strip()


def main():
    bios_str = open('/sys/devices/virtual/dmi/id/bios_version').read().strip()
    if not findall(r'[0-9]{2}[A-Z]{2,3}', bios_str):
        print('Sorry, I only understand BIOS versions in the format [0-9]{2}[A-Z]{2,3}. Yours is %s' % bios_str)
        exit(1)
    bios_version = int(findall(r'[0-9]{2}', bios_str)[0])
    bios_model = findall(r'[A-Z]{2,3}', bios_str)[0]
    print('BIOS version installed: %d (%s)' % (bios_version, bios_str))

    url = 'http://sbuservice.samsungmobile.com/BUWebServiceProc.asmx/GetContents?platformID=%s&PartNumber=AAAA' % bios_model
    max_attempts = 3
    for i in range(max_attempts):
        try:
            response = urlopen(url).read()
            break
        except IOError:
            if i < max_attempts - 1:
                sleep(1)
            else:
                print('Sorry, I tried to contact the Samsung site %d times but giving up now. Please try again later.' % max_attempts)
                exit(1)

    try:
        web_str = findall(r'<Version>([A-Z0-9]+)</Version>', str(response))[0]
        web_version = int(findall(r'[0-9]{2}', web_str)[0])
        print('BIOS version available: %d (%s)' % (web_version, web_str))

        download_filename = findall(r'<FilePathName>([A-Za-z0-9._]+)</FilePathName>', str(response))[0]
        base_url = 'http://sbuservice.samsungmobile.com/upload/BIOSUpdateItem/'
        print('Installer URL: %s%s' % (base_url, download_filename))

        if web_version > bios_version:
            print('\nBIOS UPDATE AVAILABLE!')
        else:
            print('\nYour BIOS is up to date')
    except IndexError:
        print('Sorry, got a bad response from the Samsung website:\n\n%s' % response)
        exit(1)


if __name__ == '__main__':
    main()
