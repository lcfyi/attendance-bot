<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");

    //   error_reporting(0);

    // Generate the secret on the PHP end
    if (isset($_POST['requestSecret'])) {
        // Make a secret
        $secret = randomStr();
        // Query to insert it
        $sql_query = "INSERT INTO student_info (Login_Phrase)
                        VALUES ('$secret')";
        if (mysqli_query($db, $sql_query)) {
            // Successfully added to table, return the secret
            echo "<div class='alert alert-primary status'>Success! Secret is <i>" . $secret . "</i></div>";
        } else {
            // Failed to insert the secret, probably db errors
            echo "<div class='alert alert-danger status'>Failed to insert secret</div>";
        }
    }

    // Function generates our random string
    function randomStr() {
        // Our charset
        $charSet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        // Build the string, max 6 characters
        $randStr = "";
        for ($i = 0; $i < 6; $i++) {
            $randStr .= $charSet[rand(0, strlen($charSet) - 1)];
        }
        return $randStr;
    }
?>