 $(function () {
    console.log("TEST");
        $("#successModal").on('hidden.bs.modal',function(){
            gotourl('/');
        });

        $('#successModal').on('hide.bs.modal',function(){
            gotourl('/');
        });

        $("#successmodalbtn").click(function(){
            console.log("TESTING");
            gotourl('/');
        });

        /*$("#failuremodalbtn").click(function(){
            $("#failureModal").modal('hide');
        });

        $('#menuoptionbackbtn').click(function () {
            gotourl('/');
        });


        function isEmpty(str) {
            return (!str || 0 === str.length);
        }

        function onFailure(message){
            document.getElementById("failuremessage-id").innerHTML = '<i class="fas fa-exclamation-triangle" data-fa-transform="grow-3"></i>'+ " " + message + " " + '<i class="fas fa-exclamation-triangle" data-fa-transform="grow-3"></i>';
            $('#failureModal').modal('show');
            console.log("FAILED");
        }

        /*$('#registerbtn').click(function () {
            /*var alertForm = function(message, alertClass){
                $("#logformAlert").html("<strong>" + message + "</strong>")
                $("#logformAlert").css({
                        "visibility":"visible",
                    })
                $("#logformAlert").attr("class", "alert " + alertClass)
            }
            // alert($('form').());
            $('#msg').html('');
            var user = $('#username').val();
            var pass = $('#password').val();
            var vpass = $('#validatepassword').val();
            //alert(pass + '=' + vpass)
            //alert('user is empty: ' + isEmpty(user));
            if (pass != vpass) {
                onFailure("Passwords Do No Match!");
                //alertForm("Password does not match!","alert-danger");
            }
            else if (isEmpty(user) || isEmpty(pass) || isEmpty(vpass)) {
                onFailure("Enter Username OR Password!");
                 //alertForm('Enter username or password!',"alert-danger");
            }
            else {
               var obj = { "username": user, "password": pass };
                //alert(JSON.stringify(obj));
                postFormatted('/register', obj, function (data, status) {
                    //alert(data.message +'status:'+status);
                    if (status=='success') {
                        $("#successModal").modal('show');
                        setTimeout(function(){$("#successModal").modal('hide')},5000);
                        //alertForm("Registration Success! <a href='/loginpanel'>Login Here</a>", "alert-success")
                        
                        
                    }
                }).fail(function(jqXHR, textStatus, errorThrown){
                    var responseJSON = jqXHR.responseJSON;
                    if(responseJSON){
                        var message = responseJSON.message;
                        onFailure("Registration Failed");
                        //alertForm("Registration failed. " + responseJSON.message, "alert-danger");
                    }
                    else{
                        console.log("ERROR: " + errorThrown + " " + textStatus);
                        onFailure("Registration Failed. Contact System Admin");
                        //alertForm("Registration failed. Contact System Admin.", "alert-json");
                    }
                });
                return false;
            }
        });*/
    });