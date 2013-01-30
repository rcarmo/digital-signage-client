<html lang="en">
    <head>
        <meta charset="UTF-8"/>
        <title>{{title or 'Untitled'}}</title>
        <link href="/css/common.css" rel="stylesheet"/>
%if defined('css'):
%for file in css:
        <link href="/css/{{file}}" rel="stylesheet"/>
%end
%end
%if defined('scripts'):
%for file in scripts:
    <script src="/js/{{file}}"></script>
%end
%end
  </b
    </head>
    <body style="width: {{width}}px; height: {{height}}px; overflow: hidden; display: -webkit-box; -webkit-box-pack: center; -webkit-box-align: center;">
%include
%if defined('debug'):
%if debug:
        <div class="frame1024"/>
        <div class="frame1280"/>
%end
%end
    </body>
</html>

