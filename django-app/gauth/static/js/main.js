function gmailAuthenticate(){
    console.log("e:", e)

    $.ajax({
        type: "GET",
        url: "ajax/gmailAuthenticate123",
        data: {
            uri: '/credentials'
        },
        success: function (data) {
            console.log('Done')
        }
    });
};
