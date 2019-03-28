<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");

    //   error_reporting(0);

    // Generate the secret on the PHP end
    if (isset($_POST['requestClear'])) {
        $sql_query = "UPDATE student_info SET Present = '0'";
        if (mysqli_query($db, $sql_query)) {
            echo "Success! Attendance cleared.";
        } else {
            echo "Query failed to process. Try again?";
        }
    }
?>