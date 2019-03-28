<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");

    // error_reporting(0);
    if (isset($_POST['requestTable'])) {
        if ($_POST['requestTable'] === "present") {
            $sql_query = "SELECT `studentID`, `Name`, `Photo` FROM `student_info` WHERE Present = '1'";

            // If fetch was successful, return the table
            if ($result = mysqli_query($db, $sql_query)) {
                $retTable = array();
                while ($row = mysqli_fetch_row($result)) {
                    $retTable[] = $row;
                }
                echo json_encode($retTable);
            }
        } else if ($_POST['requestTable'] === "unclaimed") {
            $sql_query = "SELECT `Login_Phrase` FROM `student_info` WHERE Needs_Update = '1'";

            // If fetch was successful, return the table
            if ($result = mysqli_query($db, $sql_query)) {
                $retTable = array();
                while ($row = mysqli_fetch_row($result)) {
                    $retTable[] = $row;
                }
                echo json_encode($retTable);
            }
        } else {
            echo "Bad request";
        }
    }
?>