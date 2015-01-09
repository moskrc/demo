<?php

Class Registry Implements ArrayAccess {
	private $vars = array();

	function __construct() {
	}

	function set($key, $var) {
		if (isset($this->vars[$key]) == true) {
			throw new Exception('Немогу установить переменную `' . $key . '`. Уже установлена.');
		}
		
		$this->vars[$key] = $var;
		return true;
	}

	function get($key) {
		if (isset($this->vars[$key]) == false) {
			return null;
		}

		return $this->vars[$key];
	}

	function remove($var) {
		unset($this->vars[$key]);
	}

	function offsetExists($offset) {
		return isset($this->vars[$offset]);
	}

	function offsetGet($offset) {
		return $this->get($offset);
	}

	function offsetSet($offset, $value) {
		$this->set($offset, $value);
	}

	function offsetUnset($offset) {
		unset($this->vars[$offset]);
	}
}

?>
