% import json
<% include('views/header.tpl', title='IIIF Fixture Repository - File Info') %>
<header>
    <div class="wrapper">
        <h1>File Information</h1>
    </div>
</header>

<div class="wrapper post">
    <div id="fileList">
        % contentType = fileInfo['type']
        % print (f"Content type: {contentType}")
        % if contentType == 'Video' or contentType == 'Audio':
            <%
                if contentType == 'Video' :
                    size = 'width="320" height="240"'
                else:
                    contentType = 'Audio'
                    size = ''
                end
                if 'internet_media_type' in fileInfo['General']:
                    mediatype = fileInfo['General']['internet_media_type']
                elif 'format' in fileInfo['General']:    
                    if "HLS" == fileInfo['General']['format']:
                        mediatype = "application/vnd.apple.mpegurl"
                        fileInfo['General']['internet_media_type'] = mediatype
                    else:
                        mediatype= fileInfo['General']['format']
                    end    
                else:
                    mediatype = "application/octet-stream"   
                end         
            %>
            
            <div width="100%" align="center">
                <video {{ size }} controls style="border:1px solid black;">
                    <source src="{{fileInfo['url']}}" type="{{ mediatype }}">
                    Your browser does not support the video tag.
                </video>
            </div>
        % elif contentType == 'Image' and not (fileInfo['name'].endswith('.vtt') or fileInfo['name'].endswith('.txt')):
            % url = fileInfo['url']
            % if 'info.json' in fileInfo:
            %   url += '/full/!500,500/0/default.jpg'
            % end
            <div width="100%" align="center">
                <div width="500px" height="500px">
                    <img src="{{ url }}" style="border:1px solid black;"/>
                </div>
            </div>
        % elif contentType == 'Model' and fileInfo['name'].endswith('.glb'):
           <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js"></script>
           <model-viewer
                src="{{fileInfo['url']}}"
                alt="{{ fileInfo['name'] }}"
                auto-rotate
                camera-controls
                style="width: 400px; height: 400px;">
            </model-viewer>
        % end 
        <br/>
        <h3>Details</h3>
        <table>
            <tr>
                <td><b>Name: </b></td><td>{{ fileInfo['name'] }}</td>
            </tr>    
            <tr>
                <td><b>Type: </b></td><td>{{ fileInfo['type'] }}</td>
            </tr>    
            <tr>
                <td><b>URL: </b></td><td><a href="{{ fileInfo['url'] }}">{{ fileInfo['url'] }}</a></td>
            </tr>    

            % for key in fileInfo.keys():
            %   if key not in ('name','url','path', 'General', 'Video', 'Audio', 'type', 'info.json', 'Image', 'Text', 'image_url', 'metadata'):
                    <tr>
                        <td><b>{{ key }}: </b></td><td>{{ fileInfo[key] }}</a></td>
                    </tr>    
                % elif key == 'image_url' and 'info.json' in fileInfo:    
                    <tr>
                        <td><b>Source Image URL: </b></td><td><a href="{{ fileInfo[key] }}">{{ fileInfo[key] }}</a></td>
                    </tr>    
                % end    
            % end    
            % if contentType == 'Video' or contentType == 'Audio':
                <tr>
                    <td><b>Type: </b></td><td>{{ fileInfo['General']['format'] }} ({{ fileInfo['General']['internet_media_type']}})</a></td>
                </tr>    
                <tr>
                    <td><b>Duration: </b></td>
                        <td>
                        % if 'duration' in fileInfo['General']:
                            {{ fileInfo['General']['duration'] / 1000 }} seconds
                        % else:
                            UNKNOWN
                        % end
                        </td>
                </tr>
                % if contentType == 'Video':
                    <tr>
                        <td><b>Width: </b></td>
                        <td>
                        % if 'Video' in fileInfo and 'width' in fileInfo['Video']:
                            {{ fileInfo['Video']['width'] }}
                        % else:
                            UNKNOWN
                        % end
                        </td>
                    </tr>
                    <tr>
                        <td><b>Height: </b></td>
                        <td>
                        % if 'Video' in fileInfo and 'height' in fileInfo['Video']:
                            {{ fileInfo['Video']['height'] }}
                        % else:
                            UNKNOWN
                        % end
                        </td>
                    </tr>
                % end    
            % end    
        </table>
        % if 'metadata' in fileInfo and fileInfo['metadata'] and 'description' in fileInfo['metadata']:
            <h3>Metadata</h3>
            <ul>
                % for key in fileInfo['metadata']['description']:
                    <li>
                        <b>{{ key[0].upper() + key[1:] }}:</b> 
                        % if fileInfo['metadata']['description'][key].startswith('http'):
                            <a href="{{ fileInfo['metadata']['description'][key] }}">{{ fileInfo['metadata']['description'][key] }}</a>
                        % else:
                            {{ fileInfo['metadata']['description'][key] }}
                        % end
                    </li>
                % end    
            </ul>
        % end    
        % if contentType != 'Other':
            <h3>JSON Resource details</h3>
            <p>The data below gives extra information on this resource and can be copied and pasted into a IIIF Manifest.</p>
            <%
                if contentType == 'Image':
                    if 'info.json' in fileInfo:
                        infoJson = fileInfo['info.json']
                    else:
                        if fileInfo['name'].endswith('.vtt'):
                            # vtt for some reason gets assigned as a image
                            infoJson = {
                                "id": fileInfo['url'],
                                "type": "Text",
                                "format": 'text/vtt'
                            }
                        elif fileInfo['name'].endswith('.txt'):    
                            infoJson = {
                                "id": fileInfo['url'],
                                "type": "Text",
                                "format": 'text/plain'
                            }
                        elif fileInfo['name'].endswith('.glb'):    
                            infoJson = {
                                "id": fileInfo['url'],
                                "type": "Model",
                                "format": "model/gltf-binary"
                            }
                        else:    
                            # straight image
                            print (json.dumps(fileInfo, indent=4))
                            infoJson = {
                                "id": fileInfo['url'],
                                "type": "Image",
                                "format": fileInfo['General']['internet_media_type'],
                                "height": fileInfo['Image']['height'],
                                "width": fileInfo['Image']['width']
                            }
                        end
                    end    
                else:
                    infoJson = {
                        'id': fileInfo['url'],
                        'type': contentType
                    }

                    if contentType == 'Video':
                        if 'Video' in fileInfo:
                            infoJson['height'] = fileInfo['Video']['height']
                            infoJson['width'] = fileInfo['Video']['width']
                        end     
                    end    
                    if 'General' in fileInfo:
                        if 'duration' in fileInfo['General']:
                            infoJson['duration'] = fileInfo['General']['duration'] / 1000
                        end
                        infoJson['format'] = fileInfo['General']['internet_media_type']
                    end
                    if contentType == 'Model' and fileInfo['name'].endswith('.glb'):
                        infoJson["format"] = "model/gltf-binary"
                    else:
                        if fileInfo['name'].endswith('.png'):
                            infoJson["format"] = "image/png"
                        end    
                        if fileInfo['name'].endswith('.hdr'):
                            infoJson["format"] = "image/vnd.radiance"
                        end    
                    end    
                end
            %>
            <pre>
{{ json.dumps(infoJson, indent=4) }}
            </pre>
        % end    
    </div>
</div>
<% include('views/footer.tpl') %>
