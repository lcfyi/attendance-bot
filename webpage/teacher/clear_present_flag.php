<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");

    // Set the Present field for entries to 0 (start of a new day, for example)
    if (isset($_POST['requestClear'])) {
        // Our query string
        $sql_query = "UPDATE student_info SET Present = '0'";
        if (mysqli_query($db, $sql_query)) {
            // Query succeeded, return success message
            echo "<div class='alert alert-primary status'>Success! Attendance cleared.</div>";
        } else {
            // Query failed, probably a bad connection to DB (is mySQL on?)
            echo "<div class='alert alert-danger status'>Query failed to process. Try again?</div>";
        }
    }
?>