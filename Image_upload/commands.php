<?php
$db = mysqli_connect("localhost", "root", "", "students");
$result = mysqli_query($db, $sql);

$sql = "INSERT INTO student_info (Login_Phrase)
            VALUES ('$lgPhrase')";
$sql = "UPDATE student_info
            SET studentID = '$stuID', Name = '$stuName', Photo = '$stuPhoto', Needs_Update = '0'
                WHERE Login_Phrase = '$lgPhrase'";

$sql = "INSERT INTO images (image, text)
            VALUES ('$image', '$image_text')";

$sql = "SELECT password FROM teachers
            WHERE teacherID = '$tchID";
?>