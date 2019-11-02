% def json2html(jsonData, level=0, path=''):
<ul>
%    for key in jsonData.keys():
%       if isinstance(jsonData[key], dict) and jsonData[key] and not 'metadata' in jsonData[key]:
%           style = ''   
%           if level < 2:
%               style = 'class="jstree-open"'
%           end 
            <li {{!style }}>{{ key }}
%                json2html(jsonData[key], level + 1, '{}/{}'.format(path,key))
            </li>
%        else:
            <li data-jstree='{ "icon" : "fa fa-file" }'><a href="info.html?file={{ path }}/{{ key }}">{{key}}</a></li>
%        end
%     end
</ul> 
% end

<% include('views/header.tpl', title='IIIF Fixture Repository') %>
        <header>
            <div class="wrapper">
                <h1>Browsing the IIIF Fixture Repository</h1>
                <p>This repository aims to store assets that can be used to create IIIF Recipes. If you are looking to create a IIIF Recipe this is a good place to start to see if there is an asset already available which you can embed into a IIIF manifest. You can see below the assets have been split into Images, Videos and Audio files, once you have navigated to a file click on it and it will take you to an information page giving you the technical details that you can embed in a Manifest.</p>
            </div>
        </header>

        <div class="wrapper post">
            <div id="fileList">
                % json2html(fileList)
            </div>
        </div>
        <script>
            $(function () {
                $('#fileList').jstree({
                        'plugins': ["wholerow"],
                        'core': {
                            'themes': {
                                'name': 'proton',
                                'responsive': true
                            },
                            'dblclick_toggle': true,
                            'expand_selected_onload': true
                        }

                }).on('changed.jstree', function (e, data) {
                    var i, j, r = [];
                    for(i = 0, j = data.selected.length; i < j; i++) {
                        var selected = data.instance.get_node(data.selected[i]);
                    }
                    var jsTree = $('#fileList').jstree(true);
                    if (jsTree.is_leaf(selected)) {
                       window.location = data.node.a_attr.href;
                    } else {
                        if (!jsTree.is_open(selected)) {
                            jsTree.open_node(selected);
                        } else {
                            jsTree.close_node(selected);
                        }
                    }    
                  }); 
            });
        </script>

<% include('views/footer.tpl') %>
