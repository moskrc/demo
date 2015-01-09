<?php
class PostModel Extends AbstractModel {

	var $id='0';
	var $name='';
	var $email='';
	var $message='';
	var $created_at='';
	var $errors=array();
	var $lastInsertId;
	
	function __construct($registry, $data=null)
	{
		//echo 'CONSTRUCT';
		parent::__construct($registry);
		
		if (is_array($data))
		{
			foreach ($data as $k => $v) {
				//echo $this->$k.''.$v;
				$this->$k=$v;
			}
		}
		
		$cmgr = ConnectionManager::getInstance();
	    $this->db = $cmgr->db;
	}
	
	function validate()
	{
    	if (!preg_match(VALID_NOT_EMPTY,$this->name))
    	{
    		$this->errors['Post']['name']='Введите имя';
    	}
		
		if (!preg_match(VALID_EMAIL,$this->email))
    	{
    		$this->errors['Post']['email']='Неверный email';
    	}
    	
		if (!preg_match(VALID_NOT_EMPTY,$this->email))
    	{
    		$this->errors['Post']['email']='Введите email';

    	}
    	
    	if (mb_strlen($this->message,'utf-8')<10)
    	{
    		$this->errors['Post']['message']='Сообщение должно быть не короче 10 знаков';
    	}
    	
    	if (mb_strlen($this->message,'utf-8')>1000)
    	{
    		$this->errors['Post']['message']='Сообщение должно быть не длинее 1000 знаков';
    	}
    	
		if (!preg_match(VALID_NOT_EMPTY,$this->message))
    	{
    		$this->errors['Post']['message']='Введите сообщение';
    	}
    	
    	
    	
    	if (empty($this->errors)) return true;
	}
	
    function getAllPosts($conditions=null)
    {
	$sql = 'SELECT id, name, email, message, created_at FROM posts ORDER BY created_at DESC';

	if ($conditions) $sql.=' '.$conditions;
	
	
    	$res = $this->db->prepare($sql);
    	$res->execute();
    	return $res->fetchAll();
    }
    
    function getImageFile()
    {
    	return site.'images'.DIRSEP.'uploaded'.$this->id;
    }
    
    function create() 
    {
    	$img = new Image($this);
    	
    	try {
			$img->openUploadedFile('userfile');
    	}
		catch (Exception $e) {
			$this->errors['Post']['userfile'] = $e->getMessage();
		}

		if (!$this->validate()) return false;
		
    	$sql = 'INSERT INTO posts (name,email,message,created_at) 
    			VALUES (:name, :email, :message, NOW())';
    	$insert = $this->db->prepare($sql);
		if($insert === false)
		{ 
			$err= $this->db->errorInfo(); 
			die($err[2]); 
		}
		    	
		$insert->bindParam(':name', $this->name, PDO::PARAM_STR);
    	$insert->bindParam(':email', $this->email, PDO::PARAM_STR);
    	$insert->bindParam(':message', $this->message, PDO::PARAM_STR);
    	
    	$res = $insert->execute();
    	
    	if ($res)
    	{
    		$this->lastInsertId =  $this->db->lastInsertId();
    		$img->saveResized(UPLOAD_IMAGE_MAX_WIDTH,UPLOAD_IMAGE_MAX_HEIGHT,$this->lastInsertId,UPLOAD_IMAGE_QUALITY, SITE_PATH.UPLOAD_IMAGE_PATH);
    	}
    	
    	return $res;
    }
    
    function getTotalRows($conditions='') {
		$sql = 'SELECT COUNT(*) FROM posts ';
		if ($conditions) $sql.=' '.$conditions;
    	$stmt = $this->db->prepare($sql);
    	$stmt->execute();
    	
    	return $stmt->fetch(PDO::FETCH_COLUMN);
    }
    	
    
}

?>