import requests
import shutil
import os
import re
from zipfile import ZipFile

class Parser:
    def __init__(self):
        self.s = requests.session()
        
    def downloadAPK(self, version):
        print('[+] Finding the current available version')
        url = 'https://apkpure.com/dragon-ball-z-dokkan-battle/com.bandainamcogames.dbzdokkanww'
        resp = self.s.get(url)
        apkPureVersion = self.getBetween(resp.text, 'version">', ' </span>')
        print(f'[+] Found version {apkPureVersion}. Checking if its a new version')
        if version < apkPureVersion:
            print(f'[+] New version detected, downloading Dokkan Battle Version {apkPureVersion}')
            url = 'https://apkpure.com/dragon-ball-z-dokkan-battle/com.bandainamcogames.dbzdokkanww/download?from=details'
            resp = self.s.get(url)
            apkLink = self.getBetween(resp.text, 'https://download.apkpure.com/', '">click')
            resp = self.s.get(f'https://download.apkpure.com/{apkLink}', stream=True)
            fileSize = int(resp.headers['Content-Length'])
            dl = 0
            with open('DokkanBattle.apk', 'wb') as f:
                for chunk in resp.iter_content(chunk_size = 1024*1024):
                    if chunk:
                        dl += len(chunk)
                        print(f'[+] {int(100 * dl / fileSize)}% Downloaded..', end='\r')
                        f.write(chunk)
            print('[+] Finished downloading. Extracting the new version code..')
        else:
            print(f'[-] Version {apkPureVersion} is not a new version, try again later.')

    def verionCode(self):
        os.rename('DokkanBattle.apk', 'DokkanBattle.zip')
        os.mkdir('data')
        ZipFile('DokkanBattle.zip').extractall('data')
        with open('data/lib/arm64-v8a/libcocos2dcpp.so', 'r', encoding='cp437') as f:
            versionCode = re.findall(r'[0-9a-f]{64}', f.read())
        return versionCode[0]

    def cleanUp(self):
        if os.path.exists('data'):
            shutil.rmtree('data')
        if os.path.exists('DokkanBattle.zip'):
            os.remove('DokkanBattle.zip')
 
    def getBetween(self, data, first, last):
        return data.split(first)[1].split(last)[0]
