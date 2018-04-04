
$(function() {

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

    // Submit post on submit
    $('#add-training-data-form').on('submit', function(event){
        event.preventDefault();
        setLoading(true);
        $.ajax({
            url: $('#add-training-data-form').attr('action'),
            type: 'POST',
            async: true,
            success: function (data) {
                setLoading(false);
                alert(data);
            },
            error: function() {
                setLoading(false);
                alert("Internal error - Please contact Nghia");
            },
            cache: false,
            contentType: false,
            processData: false
        });
    });
});