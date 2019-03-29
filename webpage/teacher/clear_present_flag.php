<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");


    // Set the Present field for entries to 0 (start of a new day)
    if (isset($_POST['requestClear'])) {
        $sql_query = "UPDATE student_info SET Present = '0'";
        if (mysqli_query($db, $sql_query)) {
            echo "<div class='alert alert-primary status'>Success! Attendance cleared.</div>";
        } else {
            echo "<div class='alert alert-danger status'>Query failed to process. Try again?</div>";
        }
    }
?>