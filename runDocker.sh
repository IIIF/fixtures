#!/bin/bash

docker build -t iiif-fixtures . && docker run -it --rm -p 8000:80 --name iiif-fixtures iiif-fixtures:latest
