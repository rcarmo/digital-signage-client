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
    <div id="qrcode" class="fixed vcenter"></div>
    <p class="message light">{{message}}</p>
</div>
%rebase layout title=title,  width=width, height=height, scripts=['jquery.min.js','jquery.qrcode.min.js'], debug=debug

