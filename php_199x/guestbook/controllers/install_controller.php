<?php

Class InstallController Extends AbstractController {

	function index() {
		$this->redirect('install/step1');
	}
	
	function step1() {
		$this->registry['template']->set ('pageTitle', 'Шаг 1/2 - Конфигурация БД');
		$this->registry['template']->show('install/step1','install');
	}
	
	function step2() {
		$this->registry['template']->set ('pageTitle', 'Шаг 2/2 - Создание администраторского аккаунта');
		$this->registry['template']->show('install/step2','install');
	}
	
	function done() {
		$this->registry['template']->set ('pageTitle', 'Все прошло успешно');
		$this->registry['template']->show('install/done','install');
	}
	
	function step1Do() {
		$this->registry['template']->set ('pageTitle', 'Шаг 1/2 - Конфигурация БД');
		
		$host = $this->data['Install']['host'];
		$login = $this->data['Install']['login'];
		$passwd = $this->data['Install']['passwd'];
		$dbname = $this->data['Install']['db'];
		
		
		
		try 
		{
			
			// Пробуем подключиться к БД
			$db = new PDO("mysql:host=$host;dbname=$dbname;charset=utf-8", $login, $passwd);
			$sql = 'SET NAMES `utf8`';
			$res = $db->prepare($sql);
			$res->execute();

		
			// ... создать файл конфигурации
			$cfg_file  = "<?php \n";
			$cfg_file .= "define('DB_HOST', '$host');\n";
			$cfg_file .= "define('DB_LOGIN', '$login');\n";
			$cfg_file .= "define('DB_PASSWD', '$passwd');\n";
			$cfg_file .= "define('DB_NAME', '$dbname');\n";
			$cfg_file .= "?>\n";
			
			file_write(CONFIG_DIR.'db.php', 'w+', $cfg_file);

		
			// .. и структуру таблиц
            $connectionManager = ConnectionManager::getInstance();
            $db = $connectionManager->db; 
			$sql = 'SET NAMES `utf8`';
			$res = $db->prepare($sql);
			$res->execute();
           
			// Читаем SQL DUMP
			$file_content = file(CONFIG_DIR.'schema.sql');
            
            $query = '';
            
            foreach($file_content as $sql_line) {
                	$tsl = trim($sql_line);
                    	if (($sql_line != '') && (substr($tsl, 0, 2) != '--') && (substr($tsl, 0, 1) != '#')) {
                        	$query .= $sql_line;
                            	if(preg_match('/;\s*$/', $sql_line)) {
                                	$query = str_replace(';', '', $query);
                                    $result = $db->query($query);
                                    $query = '';
                                }
                        }
            }
		}
		catch (Exception $e)
		{
			$this->errors['Install']=$e->getMessage();
			$this->registry['template']->set ('errors', $this->errors);
			$this->registry['template']->show('install/step1','install');
			return;
		}
		
		$this->redirect('install/step2');
	}
	
	function step2Do() {
		$this->registry['template']->set ('pageTitle', 'Шаг 2/2 - Создание администраторского аккаунта');
		
		$login = $this->data['Install']['login'];
		$email = $this->data['Install']['email'];
		$passwd = $this->data['Install']['passwd'];
		
		try
		{
			// Добавляем пользователя в БД
            $connectionManager = ConnectionManager::getInstance();
            $db = $connectionManager->db; 
			$sql = 'SET NAMES `utf8`';
			$res = $db->prepare($sql);
			$res->execute();
           
			
			$sql = "INSERT INTO users (`name`, `login`, `email`, `passwd`, `is_admin`) 
					VALUES ('Admin','$login','$email','$passwd',true)";
					
            $res = $db->prepare($sql);
            $res->execute();
            
		}
		catch (Exception $e)
		{
			$this->errors['Install']=$e->getMessage();
			$this->registry['template']->set ('errors', $this->errors);
			$this->registry['template']->show('install/step2','install');
			return;
		}
		
		$this->redirect('install/done');
	}
	
}

?>
