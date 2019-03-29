<?php
    // Create database connection
    $db = mysqli_connect("localhost", "root", "", "students");

    if (isset($_POST['requestTable'])) {
        //request entries in the format ID, Name and Photo for the present table
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
            //request entries in the format Login Phrase to show all unused login_phrases
            $sql_query = "SELECT `Login_Phrase` FROM `student_info` WHERE Needs_Update = '1' AND Name IS NULL";

            // If fetch was successful, return the table
            if ($result = mysqli_query($db, $sql_query)) {
                $retTable = array();
                while ($row = mysqli_fetch_row($result)) {
                    $retTable[] = $row;
                }
                echo json_encode($retTable);
            }
        } else if ($_POST['requestTable'] === "getAll") {
            //request entries in the format ID, Name to show the list of all registered students
            $sql_query = "SELECT `studentID`, `Name` FROM `student_info` WHERE Name IS NOT NULL";
    
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