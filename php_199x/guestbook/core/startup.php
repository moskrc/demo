<?php
error_reporting (E_ALL);
if (version_compare(phpversion(), '5.1.0', '<') == true) { die ('PHP5.1 Only'); }

// Constants:
define('VALID_EMAIL', '/\\A(?:^([a-z0-9][a-z0-9_\\-\\.\\+]*)@([a-z0-9][a-z0-9\\.\\-]{0,63}\\.(com|org|net|biz|info|name|net|pro|aero|coop|museum|[a-z]{2,4}))$)\\z/i');
define('VALID_NOT_EMPTY', '/.+/');
define('DIRSEP', DIRECTORY_SEPARATOR);

// Полный путь к проекту
$site_path = realpath(dirname(__FILE__) . DIRSEP . '..' . DIRSEP) . DIRSEP;
define ('SITE_PATH', $site_path);

define ('CONFIG_DIR', SITE_PATH.'conf'.DIRSEP);

include(CONFIG_DIR.'config.php');

// Автозагрузка классов из директории core
function __autoload($class_name) {
	$filename = strtolower($class_name) . '.php';
	$file = SITE_PATH . 'core' . DIRSEP . $filename;

	if (file_exists($file) == false) { 
		return false;
	}

	include ($file);
}

function file_write($filename, $flag, &$content) {
	if (file_exists($filename)) {
		if (!is_writable($filename)) {
			if (!@chmod($filename, 0666)) {
				throw new Exception("Cannot change mode for file ($filename)");
			};
		}
	}
	if (!$fp = @fopen($filename, $flag)) {
		throw new Exception("Cannot open file ($filename)");
	}
	if (fwrite($fp, $content) === FALSE) {
		throw new Exception("Cannot write to file ($filename)");
	}
	if (!fclose($fp)) {
		throw new Exception("Cannot close file ($filename)");
	}
}
