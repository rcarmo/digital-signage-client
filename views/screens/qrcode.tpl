<script>
    $(document).ready(function($) {
        $('#qrcode').qrcode({
            width: 512,
            height: 512,
            text: "{{code}}"
        });
    });
</script>
%include svg/simple width=width, height=height, img='ohaiqr.png'
<div id="title" class="fixed">{{title}}</div>
<div id="qrholder" class="fixed vcenter" style="text-align: center;">
    <p><div id="qrcode"></div></p>
</div>
<div class="fixed vcenter" style="top: 165px; left: 600px; width: {{width-600}}px; height: {{height-164}}px;">
    <p class="message">{{message}}</p>
</div>
%rebase layout title="QR Code",  width=width, height=height, scripts=['jquery.min.js','jquery.qrcode.min.js'], debug=debug

