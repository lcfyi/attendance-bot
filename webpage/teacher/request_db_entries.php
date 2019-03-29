<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");

    // Make sure that the POST request has the element requestTable before
    // further processing. Note that we don't allow the cilent to pass SQL
    // queries, only a single parameter so that they cannot craft their own 
    // SQL queries
    if (isset($_POST['requestTable'])) {
        //request entries in the format ID, Name and Photo for the present table
        if ($_POST['requestTable'] === "present") {
            $sql_query = "SELECT `studentID`, `Name`, `Photo` FROM `student_info` WHERE Present = '1'";

            // If fetch was successful, return the table
            if ($result = mysqli_query($db, $sql_query)) {
                // Create an array
                $retTable = array();
                // Set the array elements to each row
                while ($row = mysqli_fetch_row($result)) {
                    $retTable[] = $row;
                }
                // JSONify it
                echo json_encode($retTable);
            }
        } else if ($_POST['requestTable'] === "unclaimed") {
            // Request entries in the format Login Phrase to show all unused login_phrases
            $sql_query = "SELECT `Login_Phrase` FROM `student_info` WHERE Needs_Update = '1' AND Name IS NULL";

            // If fetch was successful, return the table
            if ($result = mysqli_query($db, $sql_query)) {
                // Create an array
                $retTable = array();
                // Set the array elements to each row
                while ($row = mysqli_fetch_row($result)) {
                    $retTable[] = $row;
                }
                // JSONify it
                echo json_encode($retTable);
            }
        } else if ($_POST['requestTable'] === "getAll") {
            // Request entries in the format ID, Name to show the list of all registered students
            $sql_query = "SELECT `studentID`, `Name` FROM `student_info` WHERE Name IS NOT NULL";
            
            // Logic same as above
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