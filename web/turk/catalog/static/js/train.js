
$(function() {
    setLoading = (isLoading) => {
        if (isLoading) {
            $('#loading').show();
        } else {
            $('#loading').hide();
        }
    };

    $(".close").click(function(){
        var img_id = $(this).attr('img-id');
        var parent = $(this).parent();
        var action = $(this).attr('action');
        console.log('Action:' + action)
        setLoading(true);
        $.ajax({
            url: action,
            type: 'POST',
            async: true,
            success: function (data) {
                parent.hide();
                setLoading(false);
            },
            error: function() {
                setLoading(false);
                alert("Not able to delete this image - Internal error");
            },
            cache: false,
            contentType: false,
            processData: false
        });
    });
});