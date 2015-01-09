<?php
require(CONFIG_DIR.'db.php');

class ConnectionManager {

	var $db;

	private static $instance;

	private function __construct(){
		$this->db = new PDO('mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf-8', DB_LOGIN, DB_PASSWD);
		$sql = 'SET NAMES `utf8`';
		$res = $this->db->prepare($sql);
		$res->execute();
	}

	public static function getInstance(){
		if(self::$instance == null){
			self::$instance = new self;
		}
		return self::$instance;
	}
}
?>
