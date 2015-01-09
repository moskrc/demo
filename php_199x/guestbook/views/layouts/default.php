<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ru" lang="ru">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>Menus</title>
	<link href="/favicon.ico" type="image/x-icon" rel="shortcut icon"/>
	<link rel="stylesheet" type="text/css" href="/css/reset.css"/>
	<link rel="stylesheet" type="text/css" href="/css/main.css"/>
	
</head>
<body>
	<div id="header">
		<a href="/" title="guestbook"><img id="logo" src="<?php echo SITE_LOGO ?>" alt="logo"/></a>
	</div>

	<div id="content">
		<?php if (isset($pageTitle)): ?>
			<H1><?php echo $pageTitle; ?></H1>
		<?php endif ?>

		<?php echo $content ?>
	</div>
	
	<div id="footer">
		All rights reserved
	</div>

</body>
</html>
