<script>
    $(document).ready(function($){
        $.ajaxSetup({async:false});
        $(".tweet").tweet({
            query: "#codebits OR #codebits2012 OR from:codebits OR to:codebits",
            avatar_size: 140,
            count: 4,
            loading_text: "loading tweets...",
            refresh_interval: 30
        });
    });
</script>
<div class="tweet" id="myDiv"></div>
%rebase layout title=title, width=width, height=height, scripts=['jquery.min.js','jquery.tweet.js'], css=['jquery.tweet.css','tweetwall.css'], debug=debug
