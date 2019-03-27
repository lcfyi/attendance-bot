<?php
#Based upon https://evertpot.com/223/
$realm = 'The batcave';

// Just a random id
$nonce = uniqid();

// Get the digest from the http header
$digest = getDigest();

// If there was no digest, show login
if (is_null($digest)) requireLogin($realm,$nonce);

$digestParts = digestParse($digest);

$user_info = array('First User' => '1234', 'Second User' =>'2345');
$user_names = array_keys($user_info);
$A1 = array();
$A2 = array();
$validResponse = array();

// Based on all the info we gathered we can figure out what the response should be
for($x=0; $x<count($user_info); $x++){
	$A1[] = md5("{$user_names[$x]}:{$realm}:{$user_info[$user_names[$x]]}");
	$A2[] = md5("{$_SERVER['REQUEST_METHOD']}:{$digestParts['uri']}");
	$validResponse[] = md5("{$A1[$x]}:{$digestParts['nonce']}:{$digestParts['nc']}:{$digestParts['cnonce']}:{$digestParts['qop']}:{$A2[$x]}");
	
}
 $count1=0;
for($x=0; $x<count($user_info); $x++){
	if ($digestParts['response']==$validResponse[$x]) {
		$count1++;
		
		echo 'Well done sir, you made it all the way through the login!';
	}
}
if ($count1<1)requireLogin($realm,$nonce);


// This function returns the digest string
function getDigest() {

    // mod_php
    if (isset($_SERVER['PHP_AUTH_DIGEST'])) {
        $digest = $_SERVER['PHP_AUTH_DIGEST'];
    // most other servers
    } elseif (isset($_SERVER['HTTP_AUTHORIZATION'])) {

            if (strpos(strtolower($_SERVER['HTTP_AUTHORIZATION']),'digest')===0)
              $digest = substr($_SERVER['HTTP_AUTHORIZATION'], 7);
    }

    return $digest;

}

// This function forces a login prompt
function requireLogin($realm,$nonce) {
    header('WWW-Authenticate: Digest realm="' . $realm . '",qop="auth",nonce="' . $nonce . '",opaque="' . md5($realm) . '"');
    header('HTTP/1.0 401 Unauthorized');
    echo 'Text to send if user hits Cancel button';
    die();
}

// This function extracts the separate values from the digest string
function digestParse($digest) {
    // protect against missing data
    $needed_parts = array('nonce'=>1, 'nc'=>1, 'cnonce'=>1, 'qop'=>1, 'username'=>1, 'uri'=>1, 'response'=>1);
    $data = array();

    preg_match_all('@(\w+)=(?:(?:")([^"]+)"|([^\s,$]+))@', $digest, $matches, PREG_SET_ORDER);

    foreach ($matches as $m) {
        $data[$m[1]] = $m[2] ? $m[2] : $m[3];
        unset($needed_parts[$m[1]]);
    }

    return $needed_parts ? false : $data;
}

?>