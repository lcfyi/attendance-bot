<?php

    $db = mysqli_connect("localhost", "root", "", "students");

    if (isset($_POST['requestUpdate'])) {
        //Set the Needs_Update field of a given entry identified by student id in the input to 1
        $stuID = mysqli_real_escape_string($db, $_POST['requestUpdate']);
        $sql_query = "UPDATE student_info SET Needs_Update=1 WHERE studentID='$stuID'";
        if ($result = mysqli_query($db, $sql_query)) {
            if (mysqli_affected_rows($db) === 1){ 
                echo "<div class='alert alert-primary status'>Success! Student with ID <i>" . $stuID . "</i> now needs to update</div>";
            } else {
                echo "<div class='alert alert-danger status'>Failed to set status, already needs update or no record found.</div>";
            }
        } else {
            //Bad request?
            echo "<div class='alert alert-danger status'>Try again later, database did not respond</div>";
        }
    } 

?>