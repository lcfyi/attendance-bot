var dict = {"efe": 12345, "oscar": "andi"};
document.getElementById('loginBtn').onmousedown = checkuser;

function checkuser(){
    var user = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    console.log(user);
    console.log(password);

    if(user == ''){
        document.getElementById('error').innerHTML="Please Enter Username";
        document.getElementById('patrick').innerHTML="Opps";
        return false;
    }
    if(password == ''){
        document.getElementById('error').innerHTML="Please Enter Password";
        document.getElementById('patrick').innerHTML="Woww";
        return false;
    }
    if(dict[user] == password){
        document.getElementById('error').innerHTML="";
        document.getElementById('patrick').innerHTML="Go to bed!!!";
        console.log("success");
        return true;
    }else{
        document.getElementById('error').innerHTML="Mismatch, Enter Again";
        document.getElementById('patrick').innerHTML="I love U";
        return false;
    }  
}