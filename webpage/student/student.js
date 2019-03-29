init = async () => {
    let constraints = {video: {width: {ideal: 2048}, height: {ideal: 2048}, facingMode: "user"}};
    navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
        let video = document.getElementById('video');
        video.srcObject = stream;
        video.play();
        video.addEventListener('loadeddata', (e) => {
            let video = document.getElementById('video');
            let canvas = document.getElementById('canvas');
            let context = canvas.getContext('2d');
            canvas.height = video.videoHeight;
            canvas.width = video.videoWidth;
            context.fillStyle = 'grey';
            context.fillRect(0, 0, canvas.width, canvas.height);
        });
    }).catch((error) => {
        window.location.href = "https://cpen291-16.ece.ubc.ca/student/";
    });

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
        xml.onreadystatechange = function() {
            if (this.status === 200 && this.readyState === 4) {
                document.getElementById("status").innerHTML = this.responseText;
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
    let retStr = "<div class='alert alert-danger'>Invalid ";
    for (let i = 0; i < retVals.length; i++) {
        if (i === 0) {
            retStr += retVals[i];
        } else {
            retStr += ", " + retVals[i];
        }
    }
    retStr += ".</div>";
    if (!valid) {
        formStatus.innerHTML = retStr;
    }
    return valid;
}
