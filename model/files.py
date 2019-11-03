#!`which python3`

from .aws import AWS
import json
from os import path
import os
from pymediainfo import MediaInfo
from botocore.exceptions import ClientError
import hashlib
import urllib.request

hostName = 'http://iiif-fixtures.s3-website-us-east-1.amazonaws.com'

def shorternFilename(filepath):
    if filepath.startswith('/'):
        filepath = filepath[1:]
    dirpath = hashlib.md5(path.dirname(filepath).encode('utf-8')).hexdigest()
    basename = path.basename(filepath)

    return "{}-{}".format(dirpath, basename.split('.')[0])

def getFileInfo(filepath):
    fileInfo = {
        'name': path.basename(filepath),
        'path': filepath,
        'url': '{}{}'.format(hostName,filepath)
    }
     
    data = getFileList()
    for filePart in filepath.split('/'):
        if filePart != '':
            data = data[filePart]
    # turn media info tracks into dict
    if 'metadata' in data:
        for key in data['metadata'].keys():
            if key != 'mediainfo':
                fileInfo[key] = data['metadata'][key]
                
        if 'mediainfo' in data['metadata'] and 'tracks' in data['metadata']['mediainfo']:
            simplifiedData = {}
            for track in data['metadata']['mediainfo']['tracks']:
                simplifiedData[track['track_type']] = track
            fileInfo.update(simplifiedData)

    print (json.dumps(fileInfo, indent=4))
    if 'Video' in fileInfo:
        fileInfo['type'] = 'Video'
    elif 'Audio' in fileInfo:
        fileInfo['type'] = 'Audio'
    else:
        fileInfo['type'] = 'Image'
        fileInfo['url'] = 'https://iiif.io/api/image/3.0/example/reference/{}'.format(shorternFilename(fileInfo['path']))
        with urllib.request.urlopen("{}/info.json".format(fileInfo['url'])) as url:
            fileInfo['info.json'] = json.loads(url.read().decode())
            
    return fileInfo

def getFileList(refresh=False):
    files = {}
    cachefile = 'files.json'
    if path.exists(cachefile) and not refresh:
        with open(cachefile) as json_data:
            files = json.load(json_data)
            json_data.close()
    else:
        files = generateFilelist()
        with open(cachefile, 'w') as json_data:
            json.dump(files, json_data)
    return files        

def addMetadataFile(s3client, filename, json_data):    
    try:
        content_object = s3client.Object('iiif-fixtures', '{}/{}'.format(os.path.dirname(filename), 'metadata.json'))
        file_content = content_object.get()['Body'].read().decode('utf-8')
        metadata = json.loads(file_content)
        print ('Data')
        print (metadata)
        json_data['metadata'].update(metadata)
    except ClientError as no_metadata_error:
        print ('No metadata file for {}'.format(filename))


def generateFilelist():
    s3client = AWS().s3()

    bucketcontents = s3client.Bucket('iiif-fixtures').objects.all()
    filesystem = {}
    for s3fileinfo in bucketcontents:
        if not s3fileinfo.key.endswith('/metadata.json'):
            path = s3fileinfo.key.split('/')
            print (s3fileinfo.key)
            dirEl = filesystem
            leaf = {}
            for pathElement in path:
                if pathElement != '':
                    if pathElement not in dirEl:
                        dirEl[pathElement] = {}
                    leaf = dirEl[pathElement]    
                    dirEl = dirEl[pathElement]
            if not s3fileinfo.key.endswith('/'):
                try: 
                    if s3fileinfo.key.startswith('video/'):
                        fileJson = json.loads(MediaInfo.parse('{}/{}'.format(hostName,s3fileinfo.key)).to_json())
                        leaf['metadata'] = { 'mediainfo': fileJson }
                    elif s3fileinfo.key.startswith('audio/') and not s3fileinfo.key.endswith('.json'):
                        fileJson = json.loads(MediaInfo.parse('{}/{}'.format(hostName,s3fileinfo.key)).to_json())
                        leaf['metadata'] = { 'mediainfo': fileJson }
                    elif s3fileinfo.key.startswith('images/') and not s3fileinfo.key.endswith('.json'):
                        leaf['metadata'] = {}
                    else:
                        print ('Failed to recognise type for {}'.format(s3fileinfo.key))
                    addMetadataFile(s3client, s3fileinfo.key, leaf)
                except OSError as configError:
                    print('Failed to analysis file due to a problem with the setup of mediainfo:')
                    print(configError)
            
    return filesystem

