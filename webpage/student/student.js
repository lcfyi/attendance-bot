var canvas = document.getElementById('canvas');
var video = document.getElementById('video');
var context = canvas.getContext('2d');

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

document.getElementById("snap").addEventListener("click", function() {
    context.drawImage(video, 20, 20, 365, 330);
    document.getElementById('patrick').innerHTML = "Awesome!";
});
