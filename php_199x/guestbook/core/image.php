<?php
class Image {

	// Первоначальное имя файла
	var $name;
	// Тип загружаемого файла
	var $type;
	// Имя во временном каталоге сервера
	var $tmp_name;
	// Первоначальный размер
	var $size;
	// Текст ошибки загрузки
	var $error;
	// Расширение
	var $extension;
	// Имя сохраняемого файла
	var $dstname;
	// Качество картинк
	var $quality = 50;
	// Исходная картинк
	var $srcimage;


	// расширение в зав. от типа
	var $extype = array(
    'image/bmp'   => 'bmp',
    'image/gif'   => 'gif',
    'image/jpeg'  => 'jpg',
    'image/pjpeg' => 'jpg',
    'image/jp2'   => 'jpg',
    'image/x-png' => 'png',
    'image/psd'   => 'psd',
    'image/tiff'  => 'tif'
    );


    function __construct()
    {

    }
     
    function openUploadedFile($inputTagName)
    {
    	if (!is_uploaded_file($_FILES[$inputTagName]['tmp_name']))
    	{
    		return;
    	}
    	 
    	if (!empty($inputTagName) || is_uploaded_file($_FILES[$inputTagName]['tmp_name']))
    	{
      if (!array_key_exists($_FILES[$inputTagName]['type'], $this->extype))
      {
      	throw new Exception('Файл не картинка');
      }

      $this->name         = $_FILES[$inputTagName]['name'];
      $this->type         = $_FILES[$inputTagName]['type'];
      $this->tmp_name     = $_FILES[$inputTagName]['tmp_name'];
      $this->size         = $_FILES[$inputTagName]['size'];
      $this->extension    = $this->extype[$this->type];

      switch ($this->type)
      {
      	case 'image/gif':
      		$this->srcimage = imagecreatefromgif($this->tmp_name);
      		break;
      	case 'image/jpeg':
      		$this->srcimage = imagecreatefromjpeg($this->tmp_name);
      		break;
      	case 'image/pjpeg':
      		$this->srcimage = imagecreatefromjpeg($this->tmp_name);
      		break;
      	case 'image/x-png':
      		$this->srcimage = imagecreatefrompng($this->tmp_name);
      		break;
      	case 'image/bmp':
      		$this->srcimage = imagecreatefromwbmp($this->tmp_name);
      		break;
      	case 'image/jp2':
      		$this->srcimage = imagecreatefromjpeg($this->tmp_name);
      		break;
      	default:
      		return false;
      		break;
      }

      if (is_resource($this->srcimage))
      {
      	return true;
      }
      else
      {
      	throw new Exception('Формат не поддерживается');
      }
    	}
    	else
    	{
    		throw new Exception('Ошибка загрузки файла');
    	}
    	return false;
    }

    function saveResized($width = 0, $height = 0, $name = '', $quality = '', $path = '')
    {
    	 
    	if (empty($this->name)) return;
    	 
    	if (empty($quality)) $quality    = $this->quality;
    	if (empty($name))    $name       = substr($this->name, 0, strrpos($this->name, "."));
    	if (empty($path))    $path       = $this->path;

    	$srcw = imagesx($this->srcimage);
    	$srch = imagesy($this->srcimage);

    	if ($width == 0 || $height == 0)
    	{
      $dstw = $srcw;
      $dsth = $srch;
    	}
    	else
    	{
      $srck = $srch/$srcw;
      $dstk = $height/$width;
      if ($srck<$dstk)
      {
      	$dstw = $width;
      	$dsth = $dstw*$srck;
      }
      else
      {
      	$dsth = $height;
      	$dstw = $dsth/$srck;
      }
    	}

    	$dstimage = imagecreatetruecolor($dstw, $dsth);

    	imagecopyresampled($dstimage, $this->srcimage, 0, 0, 0, 0, $dstw, $dsth, $srcw, $srch);


    	if (!imagejpeg($dstimage, $path.DIRSEP.$name.'.jpg', $quality))
    	throw new Exception('Ошибка сохранения картинки');
    	 
    	imagedestroy($this->srcimage);
    	imagedestroy($dstimage);

    	return true;
    }

}
?>