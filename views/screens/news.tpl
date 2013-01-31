<script>
    $(document).ready(function($){
        $.getFeed({
            url: '/feeds/{{feed}}',
            success: function(feed) {
                var html='<ul>';
                known = new Array();
                selected = new Array();
                for(var i = 0; i < feed.items.length && i < 8; i++) {
                    var item = feed.items[i];
                    /* try to de-duplicate feeds - some aggregates will throw up re-posts of the same content */
                    if($.inArray(item.title, known) != -1) { continue; }
                    known.push(item.title);
                    selected.push(item);
                }
                selected.slice(0,4).forEach(function(item){
                    html += '<li class="news" style="width: {{min(560,width/2-75)}}px;">';
                    html += '<div>';
                    html += '<div class="clamp heading">' + item.title + '</div>';
                    html += '<div class="clamp description">' + item.description + '</div>';
                    html += '</div>';
                    html += '</li>';
                });
                html += '</ul>';
                $('#result').html(html);
                // now get rid of all of the junk spacing
                $(".description").find('p').contents().unwrap();
            }
        })
    });
</script>
<div id="news">
    <div id="result"></div>
</div>
%rebase layout title=feed, width=width, height=height, scripts=['jquery.min.js','jquery.jfeed.pack.js'], css=['news.css'], debug=debug
