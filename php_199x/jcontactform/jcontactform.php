<?php
session_start();
require_once 'config.php';

if(isset($_POST['submit'])) {
	
	$response = array ('errors'=>false,'captcha'=>true, 'thank_you_message'=>$thank_you_message, 'redirect_url' => $thank_you_redirect_url,'redirect_pause' => $thank_you_redirect_pause,'redirect_message'=>$thank_you_redirect_message);
	
	
	//Check to make sure that the name field is not empty
	if(trim($_POST['contactname']) == '') {
		$response['errors'] = true;
	} else {
		$name = trim($_POST['contactname']);
	}

	//Check to make sure that the subject field is not empty
	if(trim($_POST['subject']) == '') {
		$response['errors'] = true;
	} else {
		$subject = trim($_POST['subject']);
	}

	//Check to make sure sure that a valid email address is submitted
	if(trim($_POST['email']) == '')  {
		$response['errors'] = true;
		;
	} else if (!preg_match("/^[A-Z0-9._%-]+@[A-Z0-9._%-]+\.[A-Z]{2,4}$/i", trim($_POST['email']))) {
		$response['errors'] = true;
	} else {
		$email = trim($_POST['email']);
	}

	//Check to make sure comments were entered
	if(trim($_POST['message']) == '') {
		$response['errors'] = true;
	} else {
		if(function_exists('stripslashes')) {
			$message = stripslashes(trim($_POST['message']));
		} else {
			$message = trim($_POST['message']);
		}
	}
	
	  require_once 'securimage/securimage.php';
	  $img = new Securimage;
	  if ($img->check(trim($_POST['code'])) == false) {
	  	$response['errors'] = true;
	  	$response['captcha'] = false;
	  }
	

	//If there is no error, send the email
	if(!$response['errors']) {
		$emailTo = $email_to;
		$body = "Name: $name \n\nEmail: $email \n\nSubject: $subject \n\nMessage:\n$message";
		$from = $email_from ? $email_from : $email_to;

		$headers  = 'From: '.$from." \r\n" 
		$headers .= 'Bcc: '.$email_bcc." \r\n";
		$headers .= 'Reply-To: '.$email." \r\n";
		$headers .= "Content-type: text/plain; charset=\"utf-8\" \r\n";

		mail($emailTo, $email_subject_prefix.': '.$subject, $body, $headers);
		$emailSent = true;
		
	}
	
	echo json_encode($response);
}
?>
