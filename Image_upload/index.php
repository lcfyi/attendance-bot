<?php
  // Create database connection
  $db = mysqli_connect("localhost", "root", "", "students");

  // Initialize message variable
  $msg = "";

  // If upload button is clicked ...
  if (isset($_POST['upload'])) {

		// Get student ID
		$stuID = mysqli_real_escape_string($db, $_POST['stuID']);
		// Get student name
		$stuName = mysqli_real_escape_string($db, $_POST['stuName']);
  	// Get image name
		$stuPhoto = $_FILES['image']['name'];
		// Get login phrase
		$lgPhrase = mysqli_real_escape_string($db, $_POST['lgPhrase']);
  	
		// image file directory
  	$target = "/opt/lampp/htdocs/photos/".basename($stuPhoto);

  	$sql = "UPDATE student_info
            	SET studentID = '$stuID', Name = '$stuName', Photo = '$stuPhoto', Needs_Update = '0'
                WHERE Login_Phrase = '$lgPhrase' AND Needs_Update = 1";
    //Now let's move the uploaded image into the folder 
  	if (move_uploaded_file($_FILES['image']['tmp_name'], $target)) {
      if(mysqli_query($db, $sql)) {
        $msg = "Success";
    	} else {
        $msg = "Failed to add student to database: Unknown login phrase";
    	}
  	}else{
  		$msg = "Failed to upload image";
  	}
  }
?>

<!DOCTYPE html>
<html>
<head>
<title>Image Upload</title>
<style type="text/css">
   #content{
   	width: 50%;
   	margin: 20px auto;
   	border: 1px solid #cbcbcb;
   }
   form{
   	width: 50%;
   	margin: 20px auto;
   }
   form div{
   	margin-top: 5px;
   }
   #img_div{
   	width: 80%;
   	padding: 5px;
   	margin: 15px auto;
   	border: 1px solid #cbcbcb;
   }
   #img_div:after{
   	content: "";
   	display: block;
   	clear: both;
   }
   img{
   	float: left;
   	margin: 5px;
   	width: 300px;
   	height: 140px;
   }
</style>
</head>
<body>
<div id="content">
  <form method="POST" action="index.php" enctype="multipart/form-data">
  	<input type="hidden" name="size" value="1000000">
  	<div>
  	  <input type="file" name="image">
  	</div>
  	<div>
			<input type = "text" name="stuID" ><br>
			<input type = "text" name="stuName" ><br>
			<input type = "text" name="lgPhrase" ><br>
  	</div>
  	<div>
  		<button type="submit" name="upload">POST</button>
  	</div>
  </form>
</div>
<div>
<?php
echo $msg;
?>	
</div>
</body>
</html>