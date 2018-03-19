    $('#registerbtn').click(function () {
        gotourl('/registerpanel');
    });

    $(function () {
        $('#menuoptionbackbtn').click(function () {
            gotourl('/');
        });
        function isEmpty(str) {
            return (!str || 0 === str.length);
        }
        $('#submitbtn').click(function () {
           /*var alertForm = function(message, alertClass){
                $("#logformAlert").html("<strong>" + message + "</strong>")
                $("#logformAlert").css({
                        "visibility":"visible",
                    })
                $("#logformAlert").attr("class", "alert " + alertClass)
            }*/
           // alert($('form').());
            var user = $('#username').val();
            var pass = $('#password').val();
            var obj = { "username": user, "password": pass };
            if (isEmpty(user) || isEmpty(pass)) {
                //alertForm('Enter username or password!',"alert-danger");
            }
			else{
            //alert(JSON.stringify(obj));
            postFormatted('/login', obj, function (data,status) {
                //alert(JSON.stringify(data+'status:'+status));
                if (status == 'success') {
                    //alertForm("Login Success!", "alert-success")
                    gotourl('/gameinit');
                }
                //$("#result").text(data.result);
            }).fail(function(jqXHR, textStatus, errorThrown){
                    var responseJSON = jqXHR.responseJSON;
                    if(jqXHR.responseJSON){
                        var message = responseJSON.message;
                        //alertForm("Login failed. " + responseJSON.message, "alert-danger");
                    }
                    else{
                        console.log("ERROR: " + errorThrown + " " + textStatus);
                        //alertForm("Login failed. Contact System Admin.", "alert-json");
                    }
            });
			}
            return false;
        });
        });