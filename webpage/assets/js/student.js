navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUser ||
navigator.mozGetUserMedia || navigator.msGetUserMedia;

init = () => {
    if (navigator.getUserMedia) {
        navigator.getUserMedia({video: {width: {ideal: 2048}, height: {ideal: 2048}, facingMode: "user"}}, (e) => {
            // Successfully opened stream
            let video = document.getElementById('video');
            video.srcObject = e;
            video.play();
        },
        (e) => {
            // Error opening the stream
            alert(e.name);
        });
    }

    document.getElementById("snap").addEventListener("click", (e) => {
        // Grab everything we need
        let video = document.getElementById('video');
        let canvas = document.getElementById('canvas');
        let context = canvas.getContext('2d');
        // Set the element properties, as they're 0 right now
        canvas.height = video.videoHeight;
        canvas.width = video.videoWidth;
        // Draw 1:1 of the video to the canvas
        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        // Set our hidden element to the image
        let img = document.getElementById('stuImg');
        // Append the data
        img.value = canvas.toDataURL();
    });
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
        xml.open("POST", "request_db_update.php");
        // Send the POST request
        let form = new FormData(document.getElementById("formContent"));
        xml.send(form);
    }
}

validateForm = () => {
    let stuID = document.forms['formContent']['stuID'];
    let stuName = document.forms['formContent']['stuName'];
    let lgPhrase = document.forms['formContent']['lgPhrase'];
    let stuImg = document.forms['formContent']['stuImg'];
    let formStatus = document.getElementById('status');
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
