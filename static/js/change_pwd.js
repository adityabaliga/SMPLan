function check_pwd(){
    var new_pwd = document.getElementById("new_password").value;
    var confirm_pwd = document.getElementById("confirm_password").value;

    if(new_pwd.length < 6 || confirm_pwd.length < 6){
        document.getElementById("new_password").value ="";
        document.getElementById("confirm_password").value =""
         alert("Password length should have 6 or more characters");
    }
    if(new_pwd != confirm_pwd){
        document.getElementById("new_password").value ="";
        document.getElementById("confirm_password").value =""
        alert("New password and re-entry don't match");
    }

}