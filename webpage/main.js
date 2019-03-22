document.getElementById('loginBtn').onmousedown = print;

function print(){
    var x = document.getElementById('username').value;
    console.log(x);
    var y = document.getElementById('password').value;
    console.log(y);
}