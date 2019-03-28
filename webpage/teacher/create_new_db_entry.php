<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");

    //   error_reporting(0);

    // Generate the secret on the PHP end
    if (isset($_POST['requestSecret'])) {
        $secret = randomStr();
        $sql_query = "INSERT INTO student_info (Login_Phrase)
                        VALUES ('$secret')";
        if (mysqli_query($db, $sql_query)) {
            echo "Success! Secret is <i>" . $secret . "</i>";
        } else {
            echo "Failed to insert secret";
        }
    }

    // Function generates our random string
    function randomStr() {
        $charSet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        $randStr = "";
        for ($i = 0; $i < 6; $i++) {
            $randStr .= $charSet[rand(0, strlen($charSet) - 1)];
        }
        return $randStr;
    }
?>