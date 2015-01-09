<?php

Abstract Class AbstractModel {
	protected $registry;

	function __construct($registry) {
	    $this->registry = $registry;
	}
}

?>