<?php

Abstract Class AbstractController {
	var $data=array();
	var $view=array();
	var $errors=array();
	
	protected $registry;

	function __construct($registry) {
		
	    $this->registry = $registry;
	    
	    $this->_loadModel(get_class($this));
		
		if (isset($_POST['data']))
		{
			$this->data = $_POST['data'];
			
			// Запомним что передали
		    foreach($this->data as $key=>$value) {
		    	$this->registry['template']->set($key,$value);
    		}
		}
	}
	
	abstract function index();

	function redirect($url)
	{
		header('Location: /'.$url);
	}
	
	private function _loadModel($controllerName) {
	
		$modelName = preg_replace("/Controller$/","",$controllerName);
		$modelFileName = strtolower($modelName);
	
		$path = SITE_PATH . 'models' . DIRSEP . $modelFileName . '_model.php';

		if (file_exists($path) == false) {
			trigger_error ('Модель `' . $modelName . '` не существует.', E_USER_NOTICE);
			return false;
		}
		
		include ($path);
	}
}

?>