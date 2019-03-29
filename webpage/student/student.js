// Our initialization function
init = async () => {
    //Setup webcam for students page
    let constraints = {video: {width: {ideal: 2048}, height: {ideal: 2048}, facingMode: "user"}};
    // Request the media, and handle the resolve/reject cases
    navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
        // Set the element 'video' to the stream
        let video = document.getElementById('video');
        video.srcObject = stream;
        video.play();
        // Once the video loads, also initialize our canvas object that 
        // takes a user snapshot so that it's the same height/width as the
        // device camera
        video.addEventListener('loadeddata', (e) => {
            let video = document.getElementById('video');
            let canvas = document.getElementById('canvas');
            let context = canvas.getContext('2d');
            //Initialize canvas dimensions
            canvas.height = video.videoHeight;
            canvas.width = video.videoWidth;
            context.fillStyle = 'grey';
            context.fillRect(0, 0, canvas.width, canvas.height);
        });
    }).catch((error) => {
        // Redirect the user to the secure site if there's an error
        // This is probably a poor solution and should only be used if 
        // the error was a security error, but for now it works
        window.location.href = "https://cpen291-16.ece.ubc.ca/student/";
    });

    // Add an event listener to the button to take a snapshot of the video feed
    document.getElementById("snap").addEventListener("click", (e) => {
        // Grab all required elements
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

// Handler for requesting an update to the database
// The php endpoints will have the SQL query sanitized
requestDbUpdate = () => {
    // Only update DB if all form entries are in valid format
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

// Validate the form to make sure the data isn't malformed
// Note that this does not SANITIZE input, that is done on the PHP end
validateForm = () => {
    // Grab all the elements of the form
    let stuID = document.forms['formContent']['stuID'];
    let stuName = document.forms['formContent']['stuName'];
    let lgPhrase = document.forms['formContent']['lgPhrase'];
    let stuImg = document.forms['formContent']['stuImg'];
    let formStatus = document.getElementById('status');
    let valid = true;
    let retVals = [];
    // Make sure the Student ID is a valid number
    if (stuID.value === "" || isNaN(stuID.value)) {
        valid = false;
        retVals.push("student number");
    }
    // Make sure the Student Name is a valid string (not empty)
    if (stuName.value === "") {
        valid = false;
        retVals.push("name");
    }
    // Make sure the Secret is a valid string (not empty)
    if (lgPhrase.value === "") {
        valid = false;
        retVals.push("login phrase");
    }
    // Make sure the image input is valid (not empty)
    if (stuImg.value === "") {
        valid = false;
        retVals.push("image");
    }
    // Accumulate errors and point them out
    let retStr = "<div class='alert alert-danger'>Invalid ";
    for (let i = 0; i < retVals.length; i++) {
        if (i === 0) {
            retStr += retVals[i];
        } else {
            retStr += ", " + retVals[i];
        }
    }
    retStr += ".</div>";
    // Set the status
    if (!valid) {
        formStatus.innerHTML = retStr;
    }
    // Return the success/fail of this validation
    return valid;
}
