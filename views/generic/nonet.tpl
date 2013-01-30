<html>
    <head>
        <title>{{title or 'Untitled'}}</title>
        <link rel="stylesheet" href="/css/common.css" type="text/css" media="screen" charset="utf-8">
        <!-- CSS3 neon blink -->
        <link rel="stylesheet" href="/css/neon.css" type="text/css" media="screen" charset="utf-8">
        <style>
        body {
            background: red;
            font-family: "Roboto-Bold-Condensed";
            display: -webkit-box;
            -webkit-box-pack:center; 
            -webkit-box-align:center;
            overflow: hidden;
        }
        .large {
            padding: 24px; 
            font-size: 150px;
        }
        .neon, .blink {
            font-size: 80px;
        }
        </style>
    </head>
    <body>
        <div id="panel">
            <p class="large">NO NETWORK</p>
            <p><span class="neon">NO IP ADDRESS<span class="blink"> - CHECK CABLE.</span></span></p>
        </div>
    </body>
</html>
