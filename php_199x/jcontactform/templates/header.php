<link href="/jcontactform/static/css/style.css" media="all" type="text/css" rel="stylesheet"/>

<script src="/jcontactform/static/js/jquery-1.4.2.min.js" type="text/javascript"></script>
<script src="/jcontactform/static/js/jquery.form.js" type="text/javascript"></script>
<script src="/jcontactform/static/js/jquery.validate.pack.js" type="text/javascript"></script>

<script type="text/javascript">
	$(document).ready(function(){
		$("#update_captcha_link").bind('click',function(){
			update_captcha();
			return false;
		});
	
	    $("#contactform").validate({
	    	submitHandler: function(form) {
	    		$('#contactform').ajaxSubmit({success : response, dataType:  'json' });
	    	},
	    	focusInvalid: true,
	    	focusCleanup: false
	    });

	    function response(data)
	    {
	        if (data['errors'] == true)
	        {
		        if (data['captcha'] == false)
		        {
		        	$("#captcha_error_msg").show();
		        	$("#successfull_message").hide();
		        }
	        }
	        else
	        {
	        	$("#successfull_message").html(data['thank_you_message']).show();

	        	if (data['redirect_url']!='')
	        	{
	        		$("#redirect_message").html(data['redirect_message']).show();
	        		setTimeout('location.replace("'+data['redirect_url']+'")', data['redirect_pause']);
	        	}
	        	
		        $("#contactform").hide();
	        }

			if (data)
			{
	    		update_captcha();
			}
	    }

		function update_captcha()
		{
			$("#siimage").attr('src','/jcontactform/securimage/securimage_show.php?sid=' + Math.random());
		}		    
	});
</script>
