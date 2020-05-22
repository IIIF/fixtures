#!/usr/local/bin/python3
import unittest

import os
import sys
import json
sys.path.append(".")
from model import files
from model.aws import AWS

class TestFixtures(unittest.TestCase):
    def testExistingMetadataFile(self):
        with open('tests/fixtures/existing_metadata.json') as json_file:
            data = json.load(json_file)

        s3client = AWS().s3()

        directory = 'images/Glen/photos'
        imgfiles = {
            "gottingen.jpg": { 'key', 'images/Glen/photos/gottingen.jpg' },
            "metadata.json": ""
        }

        (changed, metadata) = files.processDir(s3client, directory, imgfiles, unittest=True, metadataCache=data)
        self.assertTrue('images/Glen/photos/gottingen.jpg' in metadata, 'File not present in generated metadata') 
        self.assertTrue('attribution' in metadata['images/Glen/photos/gottingen.jpg'], 'Existing metadata not present in file') 
        self.assertEqual(metadata['images/Glen/photos/gottingen.jpg']['attribution'], 'Glen Robson, IIIF Technical Coordinator. [CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0)]', 'Existing metadata not present in file') 

    def testMixedFiles(self):        
        directory = 'video/indiana/donizetti-elixir'
        s3client = AWS().s3()
        dirFiles = {
            "act1-thumbnail.png" : "",
            "act2-thumbnail.png" : "",
            "metadata.json" : "",
            "vae0637_accessH264_low.mp4" : "",
            "vae0637_accessH264_low_act_1.mp4" : "",
            "vae0637_accessH264_low_act_2.mp4" : ""
        }

        (changed, metadata) = files.processDir(s3client, directory, dirFiles, unittest=True, metadataCache={})
        print(json.dumps(metadata, indent=4))

        self.assertTrue('video/indiana/donizetti-elixir/act1-thumbnail.png' in metadata, 'File not present in generated metadata')
        self.assertTrue('video/indiana/donizetti-elixir/vae0637_accessH264_low.mp4' in metadata, 'File not present in generated metadata')
        self.assertTrue('metadata' in metadata['video/indiana/donizetti-elixir/vae0637_accessH264_low.mp4'], 'Missing metadata')
        self.assertTrue('mediainfo' in metadata['video/indiana/donizetti-elixir/vae0637_accessH264_low.mp4']['metadata'], 'Missing mediainfo')
            
if __name__ == '__main__':
    unittest.main()
