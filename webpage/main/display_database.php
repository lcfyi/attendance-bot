<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RoboAttendance.com</title>
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

</head>
<body>
<div class="container">
  <h3>Welcome to the Display Data Page!</h3>
</div>
<div class="container">
<table class="table table-dark">
    <!-- Based upon http://www.anyexample.com/programming/php/php_mysql_example__display_table_as_html.xml-->
 <?php
 $db_host = 'localhost';
 $db_user = 'root';
 
 $database = 'students';
 $table = 'student_info';
 
 $con = mysqli_connect($db_host, $db_user,"", $database);
 if (!$con)
     die("Can't connect to database");
 
 // sending query
 $result = mysqli_query($con,"SELECT `studentID`, `Name`, `Present`, `Photo`,`Login_Phrase`, `Needs_Update`FROM {$table}");
 if (!$result) {
     die("Query to show fields from table failed");
 }
 
 $fields_num = mysqli_num_fields($result);
 $head = mysqli_fetch_fields($result);
 ?>

    <thead>
      <tr>
        <?php for($x =0 ; $x<$fields_num; $x++){ ?>
        <th scope="col"><?php echo $head[$x]->name ?> </th>
         <?php } ?>
    </tr>
    </thead>

    <tbody>
        <?php
        while($row = mysqli_fetch_row($result))
        {
        ?>
        <tr>
            <?php for($count =0; $count<3; $count++){ ?>
                <td><?php echo $row[$count] ?></td>
            <?php } ?> 
			<!---Fix image dimension so that it is resized according to display size of the tab -->
			<td> <img src= "<?php echo "http://cpen291-16.ece.ubc.ca/photos/" . $row[$count++]; ?>" width="150" height = "150" </td>
            <?php for($count=4; $count<$fields_num; $count++){ ?>
                <td><?php echo $row[$count] ?></td>
            <?php } ?> 
        
</tr>
        <?php } ?>
    </tbody>


 <?php   
 mysqli_free_result($result);
 ?>
 </table>
 </div>
 
 <div class="container">
  <h3>The camera display from the robot goes here:</h3>
	</div>

 <div>
    <!--- Div for camera display from the robot --> 
 </div>
</body>
</html>
