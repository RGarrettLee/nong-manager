import os
import json
import requests
import shutil

songsPath = os.getenv('LOCALAPPDATA') + '\\GeometryDash'
infoFile = os.path.expanduser('~/nongmanager/info.json')
backups = os.path.expanduser('~/nongmanager/nongbackups')
apiEndpoint = 'http://localhost:3000/api/nongdb'

running = True

def updateDB():
   response = requests.get(apiEndpoint)
   levels = response.json()
   return levels

def updateSaveFile(data):
   with open('{0}/info.json'.format(os.path.expanduser('~/nongmanager')), 'w') as f:
      json.dump(data, f, ensure_ascii=True, indent=4)

if (os.path.exists(os.path.expanduser('~/nongmanager'))):
   print('Files folder found. Updating with new levels...\n')
   allLevels = updateDB()
   try:
      with open('{0}/info.json'.format(os.path.expanduser('~/nongmanager')), 'r') as f:
         currentData = json.loads(f.read())

      names = []
      for level in currentData:
         names.append(level['name'])

      for level in allLevels:
         if (level['name'] not in names):
            currentData.append(level)

      updateSaveFile(currentData)
      levels = currentData
   except:
      print('info file missing, creating new one...\n')
      allLevels = updateDB()
      updateSaveFile(allLevels)
      levels = allLevels
else:
   print('Files folder does not exist, creating one...\n')
   os.mkdir(os.path.expanduser('~/nongmanager'))
   os.mkdir(os.path.expanduser('~/nongmanager/nongbackups'))
   allLevels = updateDB()
   with open('{0}/info.json'.format(os.path.expanduser('~/nongmanager')), 'w') as f:
      json.dump(allLevels, f, ensure_ascii=True, indent=4)
   levels = allLevels

def replaceWithNONG(level):
   try:
      songs = [f for f in os.listdir(songsPath) if os.path.isfile(os.path.join(songsPath, f))]
      songName = '{0}.mp3'.format(level['songID'])
      if (songName in songs and not level['active']):
         print('\nBacking up song...')
         shutil.move(f'{songsPath}/{songName}', f'{backups}/{songName}')
         print('Replacing song with ID - {0} with NONG song on level - {1}...'.format(level['songID'], level['name']))
         response = requests.get(level['replacementLink'])
         open('{0}/{1}'.format(songsPath, songName), 'wb').write(response.content)
         level['active'] = True
         print('Song Replaced!\n')
         updateSaveFile(levels)
      else:
         print('Could not find song OR song has been replaced!')
   except:
      print('Error encountered replacing the song for level - {0}'.format(level['name']))
      shutil.move(f'{backups}/{songName}', f'{songsPath}/{songName}')

def restoreSong(level):
   try:
      songName = '{0}.mp3'.format(level['songID'])
      if (level['active']):
         print('\nRestoring song...')
         os.remove(f'{songsPath}/{songName}')
         shutil.move(f'{backups}/{songName}', f'{songsPath}/{songName}')
         level['active'] = False
         print('Song Restored!\n')
         updateSaveFile(levels)
      else:
         print('Original song is being used')
   except:
      print('Error encountered restoring song')

print('\nWelcome to the NONG Manager\n--THIS WILL BECOME A GUI APPLICATION--\n')
while (running):
   resp = input('Select an option:\n1: Replace\n2: Restore\n3: Exit\n')
   if (resp == '1'):
      replaceWithNONG(levels[2])
   elif (resp == '2'):
      restoreSong(levels[2])
   elif (resp == '3'):
      running = False