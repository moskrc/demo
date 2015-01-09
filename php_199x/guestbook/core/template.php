<?php

Class Template {
	private $registry;
	private $vars = array();

	function __construct($registry) {
		$this->registry = $registry;
	}

	function set($varname, $value, $overwrite=false) {
		if (isset($this->vars[$varname]) == true AND $overwrite == false) {
			trigger_error ('Невозможно установить переменную `' . $varname . '`. Уже установлена и не подлежит перезаписи.', E_USER_NOTICE);
			return false;
		}

		$this->vars[$varname] = $value;
		return true;
	}

	function remove($varname) {
		unset($this->vars[$varname]);
		return true;
	}

	function show($name, $layout='default') {
		$path = SITE_PATH . 'views' . DIRSEP .$name . '.php';

		if (file_exists($path) == false) {
			trigger_error ('Вид `' . $name . '` не существует.', E_USER_NOTICE);
			return false;
		}

		// Load variables
		foreach ($this->vars as $key => $value) {
			$$key = $value;
		}

		// Обработка страницы для включения в шаблон
		
		ob_start();

		include ($path);

		$out = ob_get_clean();

		$content = $out;

		include (SITE_PATH . 'views' . DIRSEP . 'layouts'. DIRSEP .$layout.'.php');
	}

}

?>
