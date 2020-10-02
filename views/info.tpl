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
        % if contentType == 'Video' or contentType == 'Audio':
            <%
                if contentType == 'Video' :
                    size = 'width="320" height="240"'
                else:
                    contentType = 'Audio'
                    size = ''
                end
            %>
            
            <div width="100%" align="center">
                <video {{ size }} controls style="border:1px solid black;">
                    <source src="{{fileInfo['url']}}" type="{{ fileInfo['General']['internet_media_type'] }}">
                    Your browser does not support the video tag.
                </video>
            </div>
        % else:
            % url = fileInfo['url']
            % if 'info.json' in fileInfo:
            %   url += '/full/!500,500/0/default.jpg'
            % end
            <div width="100%" align="center">
                <div width="500px" height="500px">
                    <img src="{{ url }}" style="border:1px solid black;"/>
                </div>
            </div>
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
                    <td><b>Duration: </b></td><td>{{ fileInfo['General']['duration'] / 1000 }} seconds</a></td>
                </tr>
                % if contentType == 'Video':
                    <tr>
                        <td><b>Width: </b></td><td>{{ fileInfo['Video']['width'] }} </a></td>
                    </tr>
                    <tr>
                        <td><b>Height: </b></td><td>{{ fileInfo['Video']['height'] }}</a></td>
                    </tr>
                % end    
            % end    
        </table>
        % if 'metadata' in fileInfo and fileInfo['metadata']:
            <h3>Metadata</h3>
            <table>
                % for key in fileInfo['metadata']:
                    <tr>
                        <td><b>{{ key[0].upper() + key[1:] }}: </b></td><td>{{ fileInfo['metadata'][key] }}</td>
                    </tr>
                % end    
            </table>
        % end    
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
                    infoJson['height'] = fileInfo['Video']['height']
                    infoJson['width'] = fileInfo['Video']['width']
                end    
                if 'General' in fileInfo:
                    infoJson['duration'] = fileInfo['General']['duration'] / 1000
                    infoJson['format'] = fileInfo['General']['internet_media_type']
                end
            end
        %>
        <pre>
{{ json.dumps(infoJson, indent=4) }}
        </pre>
    </div>
</div>
<% include('views/footer.tpl') %>
