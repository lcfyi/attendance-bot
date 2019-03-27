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

requestDbUpdate = () => {
    if (validateForm()) {
        let xml = new XMLHttpRequest();
        // Add an event listener to update
        xml.onreadystatechange = (e) => {
            if (xml.status === 200) {
                console.log(xml.status);
                console.log(xml.responseText);
                document.getElementById("status").innerHTML = xml.responseText;
            }
        };
        // Open the POST request
        xml.open("POST", window.location.href + "/request_db_update.php");
        // Send the POST request
        let form = new FormData(document.getElementById("formContent"));
        xml.send(form);
    }
}

document.getElementById("snap").addEventListener("click", function() {
    context.drawImage(video, 20, 20, 365, 330);
    document.getElementById('patrick').innerHTML = "Awesome!";
    let img = document.getElementById('stuImg');
    img.value = canvas.toDataURL();
});

validateForm = () => {
    let stuID = document.forms['formContent']['stuID'];
    let stuName = document.forms['formContent']['stuName'];
    let lgPhrase = document.forms['formContent']['lgPhrase'];
    let stuImg = document.forms['formContent']['stuImg'];
    let formStatus = document.getElementById('formStatus');
    let valid = true;
    let retVals = [];
    if (stuID.value === "" || isNaN(stuID.value)) {
        valid = false;
        retVals.push("student number");
    }
    if (stuName.value === "") {
        valid = false;
        retVals.push("name");
    }
    if (lgPhrase.value === "") {
        valid = false;
        retVals.push("login phrase");
    }
    if (stuImg.value === "") {
        valid = false;
        retVals.push("image");
    }
    let retStr = "Invalid ";
    for (let i = 0; i < retVals.length; i++) {
        if (i === 0) {
            retStr += retVals[i];
        } else {
            retStr += ", " + retVals[i];
        }
    }
    retStr += ".";
    if (!valid) {
        formStatus.innerHTML = retStr;
    } else {
        formStatus.innerHTML = "";
    }
    return valid;
}
