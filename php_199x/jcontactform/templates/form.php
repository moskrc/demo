
<div id="title"><h1>jContactForm</h1></div>
<div id="contact-wrapper">
	
	<div id="successfull_message" style="display:none;">
	</div>

	<div id="redirect_message" style="display:none;">
	</div>
	
	<form method="post" action="/jcontactform/jcontactform.php" id="contactform">
		<div>
		    <label for="name"><strong>Name:</strong></label>
			<input type="text" size="50" name="contactname" id="contactname" value="" class="required" />
		</div>
	
		<div>
			<label for="email"><strong>Email:</strong></label>
			<input type="text" size="50" name="email" id="email" value="" class="required email" />
		</div>
	
		<div>
			<label for="subject"><strong>Subject:</strong></label>
			<input type="text" size="50" name="subject" id="subject" value="" class="required" />
		</div>
	
		<div>
			<label for="message"><strong>Message:</strong></label>
			<textarea rows="5" cols="50" name="message" id="message" class="required"></textarea>
		</div>
	
		<div>
			<label for="captcha_image"><strong>Security Code:</strong></label>
			<img id="siimage" src="/jcontactform/securimage/securimage_show.php" alt="CAPTCHA Image" />
			<a id="update_captcha_link" tabindex="-1" style="border-style: none" href="#" title="Refresh Image"><img src="/jcontactform/securimage/images/refresh.gif" alt="Reload Image" border="0" onclick="this.blur()" align="bottom" /></a>
		</div>
		
		<div>
			<label for="captcha_code"><strong>Verify Code:</strong></label>
			<input type="text" name="code" size="8" />
			<label id="captcha_error_msg" for="captcha_code" generated="true" class="error" style="display: none;">Please enter a valid verify code.</label>
		</div>		
		
		<div id="submit_block">
	    <input id="submit_button" type="submit" value="Send Message" name="submit" />
	    </div>
    </form>
    
</div>
