var dict = {"efe": 123};
document.getElementById('loginBtn').onmousedown = checkuser;
document.getElementById('switching').onclick = switching;

function validate(){
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
        //document.getElementById('patrick').innerHTML="Go to bed!!!";
        console.log("success");
        return true;
    }else{
        document.getElementById('error').innerHTML="Mismatch, Enter Again";
        document.getElementById('patrick').innerHTML="I love U";
        return false;
    }  
}

function checkuser(){
    if(validate())
    window.location.href = '../main/display_test.php';
}

function switching(){
    window.location.href = '../student_login/student.html';
}