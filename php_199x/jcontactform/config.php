<?php
/* ------------------------------------------------------------------------ */
/* 	Script configuration - refer README.txt									*/
/* ------------------------------------------------------------------------ */

/* Email address where the messages should be delivered */
$email_to = 'admin@site.com';
$email_bcc = 'other@account.com';

/* From email address, in case your server prohibits sending emails from addresses other than those of your 
own domain (e.g. email@yourdomain.com). If this is used then all email messages from your contact form will appear 
from this address instead of actual sender. */
$email_from = '';

/* This will be appended to the subject of contact form message */
$email_subject_prefix = 'Feedback from site.com';

/* Thank you message to be displayed after the form is submitted. Can include HTML tags. */
$thank_you_message = <<<EOD
<p><strong>Email Successfully Sent!</strong></p>
<p style="color: #333;">Thank you for using my contact form! Your email was successfully sent and I will be in touch with you soon.</p>
EOD;

/* URL to be redirected to after the form is submitted. Work if not empty. */
$thank_you_redirect_url = '';
$thank_you_redirect_pause = 5;
$thank_you_redirect_message = <<<EOD
<p style="color: #333;">After 5 seconds you will be moved to othersite.com...</p>
EOD;
?>
