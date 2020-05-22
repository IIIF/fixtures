#!/bin/bash

docker build -t iiif-fixtures . && docker run -it --rm -p 8000:80 -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" --name iiif-fixtures iiif-fixtures:latest
