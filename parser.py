import requests
import os
import shutil
import re
import sys
import json
from zipfile import ZipFile

class Update:
    def __init__(self, version, server):
        self.s = requests.session()
        self.version = version
        self.server = server

    def downloadAPK(self):
        if self.server == 'ishin-global.aktsk.com':
            _Package = 'https://api.qoo-app.com/v6/apps/com.bandainamcogames.dbzdokkanww/download?version_code='
            _Page = 'https://apps.qoo-app.com/en/app/2519'
        else:
            _Package = 'https://api.qoo-app.com/v6/apps/com.bandainamcogames.dbzdokkan/download?version_code='
            _Page = 'https://apps.qoo-app.com/en/app/191'
        resp = self.s.get(_Page)
        _QooVersion = self.getBetween(resp.text, 'softwareVersion":"', '","fileSize"')
        if _QooVersion != self.version:
            resp = self.s.get('https://api.qoo-app.com/v6/apps')
            try:
                _VersionCode = resp.json()['apps'][0]['version_code']
            except KeyError:
                _VersionCode = 999
            _Package = _Package + str(_VersionCode)
            resp = self.s.get(_Package, stream = True)
            _FileSize = int(resp.headers['Content-Length'])
            _Download = 0
            if _FileSize < 80000000:
                print('[-] Incorrect file size, Qoo probably changed the download properties. Press enter to exit!')
                input()
                sys.exit()
            with open('DokkanBattle.apk', 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024*1024):
                    if chunk:
                        _Download += len(chunk)
                        print(f'[+] {int(100 * _Download / _FileSize)}% Downloaded..', end='\r')
                        f.write(chunk)
            print('[+] Finished downloading.')
            _ClientVersion = self.extractClient(_QooVersion)
            return _ClientVersion
        else:
            print('[-] A new version doesn\'t exist..')

    def extractClient(self, _version):
        os.rename('DokkanBattle.apk', 'DokkanBattle.zip')
        os.mkdir('APK')
        ZipFile('DokkanBattle.zip').extractall('APK')
        with open('APK/lib/armeabi-v7a/libcocos2dcpp.so', 'r', encoding='cp437') as f:
            _VersionCode = re.findall(r'[0-9a-f]{64}', f.read())
            for data in _VersionCode:
                if not data.isdigit():
                    return f'{_version}-{data}'

    def cleanUp(self):
        if os.path.exists('APK'):
            shutil.rmtree('APK')
        if os.path.exists('DokkanBattle.zip'):
            os.remove('DokkanBattle.zip')

    def getBetween(self, data, first, last):
        return data.split(first)[1].split(last)[0]
