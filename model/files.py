#!`which python3`

from .aws import AWS
import json
from os import path
import os
from pymediainfo import MediaInfo
from botocore.exceptions import ClientError
import hashlib
import urllib.request
from urllib.error import HTTPError

hostName = 'https://fixtures.iiif.io'

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
        fileInfo['metadata'] = {}
        for key in data['metadata'].keys():
            if key != 'mediainfo':
                fileInfo['metadata'][key] = data['metadata'][key]
                
        if 'mediainfo' in data['metadata'] and 'tracks' in data['metadata']['mediainfo']:
            simplifiedData = {}
            for track in data['metadata']['mediainfo']['tracks']:
                simplifiedData[track['track_type']] = track
            fileInfo.update(simplifiedData)

    print (fileInfo['path'])
    if 'Video' in fileInfo:
        fileInfo['type'] = 'Video'
    elif 'Audio' in fileInfo:
        fileInfo['type'] = 'Audio'
    elif fileInfo['path'].startswith('/3d'):    
        fileInfo['type'] = 'Model'
    elif fileInfo['path'].startswith('/other'):    
        fileInfo['type'] = 'Other'
    else:
        fileInfo['type'] = 'Image'
        fileInfo['image_url'] = '{}{}'.format(hostName,filepath)
        try:
            fileInfo['url'] = 'https://iiif.io/api/image/3.0/example/reference/{}'.format(shorternFilename(fileInfo['path']))
            with urllib.request.urlopen("{}/info.json".format(fileInfo['url'])) as url:
                fileInfo['info.json'] = json.loads(url.read().decode())
        except HTTPError as error:
            print ('Failed to get info.json at {}. Treat as flat image'.format(fileInfo['url']))
            fileInfo['url'] = '{}{}'.format(hostName,filepath)
            
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
        print (os.path.realpath(cachefile))
        with open(cachefile, 'w') as json_data:
            json.dump(files, json_data)
    return files        

def getMetadataFile(s3client, directory):    
    metadata = {} 
    filename = '{}/metadata.json'.format(directory)
    try:
        content_object = s3client.Object('iiif-fixtures', filename)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        metadata = json.loads(file_content)
    except ClientError as no_metadata_error:
        print ('No metadata file for {}'.format(filename))

    return metadata

def saveMetadata(directory, metadata):
    metadataFilename = '{}/{}'.format(directory, 'metadata.json')
    print ('Updating: {}'.format(metadataFilename))
    test=True
    if not test:
        s3cli = AWS().client('s3',region='us-east-1')
        s3cli.put_object(ACL='private', Body=json.dumps(metadata).encode('utf-8'), Bucket='iiif-fixtures', Key=metadataFilename, ContentType='application/json', ContentDisposition='inline')    

def processDir(s3client, directory, files, unittest=False, metadataCache=None):
    if metadataCache:
        metadata = metadataCache
    else:    
        metadata = getMetadataFile(s3client, directory)
    metadataChange=False
    filesystem = {}
    for filename in files:
        s3fileinfo = files[filename]    
        fullpath = "{}/{}".format(directory, filename)
        if not filename.endswith('metadata.json'):
            path = fullpath.split('/')
            dirEl = filesystem
            leaf = {}
            for pathElement in path:
                if pathElement != '':
                    if pathElement not in dirEl:
                        dirEl[pathElement] = {}
                    leaf = dirEl[pathElement]    
                    dirEl = dirEl[pathElement]

            try: 
                if fullpath in metadata and 'metadata' in metadata[fullpath]:
                    leaf['metadata'] = {}
                    for key in  metadata[fullpath]['metadata']:
                        leaf['metadata'][key] = metadata[fullpath]['metadata'][key]
                if (directory.startswith('video/') or directory.startswith('audio/')) and ('metadata' not in leaf or 'mediainfo' not in leaf['metadata']):
                    print ('Media info not found so adding')
                    fileJson = json.loads(MediaInfo.parse('{}/{}'.format(hostName,fullpath)).to_json())
                    leaf['metadata'] = { 'mediainfo': fileJson }

                    if fullpath not in metadata:
                        metadata[fullpath] = {}
                    if 'metadata' not in metadata[fullpath]:
                        metadata[fullpath]['metadata'] = {}

                    metadata[fullpath]['metadata']['mediainfo'] =  fileJson
                    metadataChange=True
                
            except OSError as configError:
                print('Failed to analysis file due to a problem with the setup of mediainfo:')
                print(configError)
    if not unittest and metadataChange:
        # save metadata to s3 
        saveMetadata(directory, metadata)
            
    if unittest:
        return (metadataChange, metadata)
    else:
        return filesystem

def recursiveMergeDicts(sourceDict, newDict):
    for key in newDict:
        if key not in sourceDict:
            sourceDict[key] = newDict[key]
        else:
            recursiveMergeDicts(sourceDict[key], newDict[key])


def generateFilelist():
    s3client = AWS().s3()

    bucketcontents = s3client.Bucket('iiif-fixtures').objects.all()
    filesystem = {}
    # turn in to a dict of files and folders
    filesDict = {}
    for s3fileinfo in bucketcontents:
        if os.path.basename(s3fileinfo.key):
            directory = os.path.dirname(s3fileinfo.key)
            if directory not in filesDict:
                filesDict[directory] = {}

            filesDict[directory][os.path.basename(s3fileinfo.key)] = s3fileinfo    

    metadata = {}
    for dirName in filesDict:        
        dirInfo = processDir(s3client, dirName, filesDict[dirName])
        recursiveMergeDicts(metadata, dirInfo)
            
    return metadata
        
