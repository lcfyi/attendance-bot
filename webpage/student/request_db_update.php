<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");

    // error_reporting(0);

    // Check if the proper keys are in the POST request
    if (isset($_POST['stuID']) && isset($_POST['stuName']) 
        && isset($_POST['lgPhrase']) && isset($_POST['image'])) {
		// Get student ID, escaping the nasty strings
		$stuID = mysqli_real_escape_string($db, $_POST['stuID']);
		// Get student name, same deal
		$stuName = mysqli_real_escape_string($db, $_POST['stuName']);
  	    // This will be sent as a Base64 request, we must decode it to form the image
        $base64StuPhoto = $_POST['image'];
        // Split the string between the base64;image/png and the actual payload
        $stuPhotoArray = explode(',', $base64StuPhoto);
        // Replace all spaces so we can actually interpret the data
        $stuPhotoData = str_replace(' ', '+', $stuPhotoArray[1]);
		// Get login phrase
		$lgPhrase = mysqli_real_escape_string($db, $_POST['lgPhrase']);
        // image file directory
  	    $target = "/opt/lampp/htdocs/photos/". $stuID . ".png";

        $sql_query = "SELECT * FROM student_info WHERE Needs_Update = '1' 
                AND Login_Phrase = '$lgPhrase'";
        
        // Filename 
        $filename = $stuID . ".png";
        // Update phrase
  	    $sql_update = "UPDATE student_info
            	SET studentID = '$stuID', Name = '$stuName', Photo = '$filename', Needs_Update = '0'
                WHERE Login_Phrase = '$lgPhrase' AND Needs_Update = 1";
    
        // Store the image in place, if successful then do additional stuff
        if ($result = mysqli_query($db, $sql_query)) {
            if (mysqli_num_rows($result) === 1) {
                if(file_put_contents($target, base64_decode($stuPhotoData))) {
                    // Create the image, if the query was successful
                    if (mysqli_query($db, $sql_update)) {
                        echo "<div class='alert alert-primary'>Success!</div>";
                    } else {
                        echo "<div class='alert alert-danger'>Database update error, potentially duplicate student ID?</div>";
                    }
                // File upload failed, delete the file if it's been made
                } else {
                    if (file_exists($target)) {
                        unlink($target);
                        echo "<div class='alert alert-danger'>File upload failed, creation reverted.</div>";
                    } else {
                        echo "<div class='alert alert-danger'>File upload failed, no file created.</div>";
                    }
                }
            } else {
                echo "<div class='alert alert-warning'>Secret does not exist or update not necessary.</div>";
            }
        }
    }
?>