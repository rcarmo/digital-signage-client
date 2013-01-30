<script>
    $(document).ready(function($) {
        $('#qrcode').qrcode({
            width: 512,
            height: 512,
            text: "{{code}}"
        });
    });
</script>
<div class="container">
<div id="title" class="branding">{{title}}</div>
<div id="qrholder" class="fixed vcenter hcenter">
    <div id="qrcode" class="fixed vcenter"></div>
</div>
<div class="fixed vcenter" style="top: 165px; left: 600px; width: {{width-600}}px; height: {{height-164}}px;">
    <p class="message">{{message}}</p>
</div>
</div>
%rebase layout title="QR Code",  width=width, height=height, scripts=['jquery.min.js','jquery.qrcode.min.js'], debug=debug

