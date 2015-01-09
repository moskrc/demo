<?php

Class Router {
	private $registry;
	private $path;
	private $args = array();

	function __construct($registry) {
		$this->registry = $registry;
	}

	function setPath($path) {
		$path .= DIRSEP;

		if (is_dir($path) == false) {
			throw new Exception ('Неверный путь к контроллерам: `' . $path . '`');
		}

		$this->path = $path;
	}

	function getArg($key) {
		if (!isset($this->args[$key])) { return null; }
		return $this->args[$key];
	}

	function delegate() {

		$this->_getController($file, $controller, $action, $args);

		if (!is_readable(CONFIG_DIR.'db.php'))
		{
			$file = $this->path.'install_controller.php';
			$controller = 'Install';
		}

		if (is_readable($file) == false) {
			$this->_notFound('Файл контроллера не найден');
		}
	
		// Подключаем
		include ($file);

		// Создаем
		$class = $controller.'Controller';
		$controller = new $class($this->registry);

		// Проверям на action
		if (is_callable(array($controller, $action)) == false) {
			$this->_notFound('Действие не найдено');
		}

		// Запускаем действие
		$controller->$action();
	}

	private function _extractArgs($args) {
		if (count($args) == 0) { return false; }
		$this->args = $args;
	}

	private function _getController(&$file, &$controller, &$action, &$args) {
		$route = (empty($_GET['route'])) ? '' : $_GET['route'];
			
		if (empty($route)) { $route = 'post'; }

		$route = trim($route, '/\\');
		$parts = explode('/', $route);

		// Ищем имя контроллера
		$cmd_path = $this->path;
		foreach ($parts as $part) {
			$fullpath = $cmd_path . $part;
				
			if (is_dir($fullpath)) {
				$cmd_path .= $part . DIRSEP;
				array_shift($parts);
				continue;
			}
				
			// Файл контроллера
			if (is_file($fullpath . '_controller.php')) {
				$controller = $part;
				array_shift($parts);
				break;
			}
		}

		// Опр. действие
		$action = array_shift($parts);
		if (empty($action)) { $action = 'index'; }

		$file = $cmd_path . $controller . '_controller.php';
		$args = $parts;
	}

	private function _notFound($message) {
		die($message);
	}
}

?>
