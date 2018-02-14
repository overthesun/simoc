// JavaScript source code
DATA_FORMAT_URL = "/data_format"

// Synchronous ajax request to get the message data format
const MESSAGE_DATA_FORMAT = $.post({
        type: "GET",
        url: DATA_FORMAT_URL,
        async: false
    }).responseText;


function convertMsgPack(data){
    try{
        value = msgpack.decode(new Uint8Array(data));
    } catch(err){
        console.log(err);
    }
    return value;
}


function ajaxFormatted(url, data, options){
    var addOptions = options;
    if (MESSAGE_DATA_FORMAT === "msgpack") {
        var options = {
            url:url,
            converters: {
                // convert to "json" (actually msgpack)
                "binary json": convertMsgPack,
            },
            contents:{
                msgpack:/msgpack/,
            },
            accepts:{
                msgpack:"application/x-msgpack",
            },
            // Accept "json" (actually msgpack) so that jquery will give us the data
            // on error
            dataType:"json",
            xhr:function(){
                try {
                    var xhr = new window.XMLHttpRequest();
                    xhr.responseType = "arraybuffer";
                    return xhr
                } catch ( e ) {}
            },
        }
        if(data){
            $.extend(options, {
                contentType: "application/x-msgpack",
                data: msgpack.encode(data),
                processData: false
            });
        }

        $.extend(options, addOptions);

        return $.ajax(options);
    }

    else if(MESSAGE_DATA_FORMAT === "json"){
        var options = {
            url: url,
            dataType:"json",
            }

        if(data){
            $.extend(options, {
                data:JSON.stringify(data),
                contentType:"application/json",
            });
        }

        $.extend(options, addOptions);

        return $.ajax(options);
    }
    else {
        throw new Exception("Unknown message data format: " + MESSAGE_DATA_FORMAT)
    }
}


function postFormatted(url, data, callback){
    return ajaxFormatted(url, data, {
        method:"POST",
        success: callback
    });
}

function getFormatted(url, callback){
    return ajaxFormatted(url, null, {
        method:"GET",
        success: callback
    });
}