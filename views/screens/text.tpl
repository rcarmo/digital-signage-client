%include svg/simple width=width, height=height
<div id="title" class="fixed">{{title}}</div>
<div class="fixed vcenter" style="top: 165px; left: 0px; width: {{width}}px; height: {{height-164}}px;">
    <p class="message">{{message}}</p>
</div>
%rebase layout title="Text", width=width, height=height, debug=debug