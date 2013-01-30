<html>
    <head>
        <title>{{title or 'Untitled'}}</title>
        <link rel="stylesheet" href="/css/common.css" type="text/css" media="screen" charset="utf-8">
        <style>
        body {
            background: green;
             display: -webkit-box;
             -webkit-box-pack:center; 
             -webkit-box-align:center;
        }
        </style>
    </head>
    <body style="width: {{width}}px; height: {{height}}px; overflow: hidden;">
        <div id="panel" class="vcenter">
            <p class="branding">I'M HERE!</p>
            <p><span class="number">{{ip_address}}</span></p>
            <p>Client version {{version}}</span></p>
        </div>
    </body>
</html>
