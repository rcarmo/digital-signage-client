<div class="container">
    <h1>Local Routes</h1>
<p>This page lists the currently active routes on the local HTTP server:</p>
<ul>
% for module in modules.keys():
<li class="module">
    <dt>{{module}}<dt>
    <ul class="routes">
% for route in modules[module]:
    <li class="route"><tt>{{route['route']}}</tt></li>
    <dt>{{route['doc']}}</dt>
% end        
    </ul>
</li>
% end
</div>
%rebase layout title=title, width=width, height=height, debug=debug