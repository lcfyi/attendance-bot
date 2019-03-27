<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OscarEfe.com</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

</head>
<body>
 

<?php

$fields_num = 4;
$row_count=3;
$db = array(
    array("ID", "name","surname", "present"),
    array("1","efe","evci","y"),
    array("2","torin","s","n"),
   array( "3","oscar","q","n")
);
?>
<div class="container">
<table class="table">
    
    <thead>
      <tr>
        <?php for($x =0 ; $x<$fields_num; $x++){ ?>
        <th scope="col"><?php echo $db[0][$x] ?> </th>
        <?php } ?>
    </tr>
    </thead>

    <tbody>
        <?php for($row_index =1; $row_index<$row_count+1; $row_index++) { ?>
        <tr>
            <?php for($count =0; $count<$fields_num; $count++){ ?>
                <td><?php echo $db[$row_index][$count] ?></td>
                <?php } ?>
        </tr>
        <?php } ?>
    </tbody>
</table>
</div>

 
</body>
</html>
