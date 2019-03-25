var video = document.getElementById('video');

navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUser ||
navigator.mozGetUserMedia || navigator.msGetUserMedia;

if(navigator.getUserMedia){
    navigator.getUserMedia({video:true},streamWebCam,throwError);
}

function streamWebCam(stream){
    video.srcObject=stream;
    video.play();
}

function throwError(e){
    alert(e.name);
}

function switching(){
    var p = document.getElementById('status');
    p.innerHTML = "Authorized";
    p.style.backgroundColor = "#008000";
    p.style.borderColor = "#008000";   

    var p = document.getElementById('door');
    p.innerHTML = "Open";
    p.style.backgroundColor = "#008000";
    p.style.borderColor = "#008000";  
    
    document.getElementById('patrick').innerHTML = "Congrats!";
}