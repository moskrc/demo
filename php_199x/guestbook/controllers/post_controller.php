<?php

Class PostController Extends AbstractController {

	function index() {
		$this->registry['template']->set ('pageTitle', 'Список постов');
		
		$post = new PostModel($this->registry);
		
		$paginator = new Paginator($post,'getAllPosts');
		
		$posts = $paginator->getPages();
		
		$this->registry['template']->set ('paginator', $paginator);
		
		
		$this->registry['template']->set ('posts', $posts);
		$this->registry['template']->show('post/index');
	}
	
	
	function add() {
		$this->registry['template']->set ('pageTitle', 'Новая запись');
		
		if (!empty($this->data))
		{
			$post = new PostModel($this->registry, $this->data['Post']);
			
			if ($post->create())
			{
				$this->redirect('post/index');
			}
			else
			{
				$this->errors = array_merge_recursive($post->errors, $this->errors);
				$this->registry['template']->set ('errors', $this->errors);
				$this->registry['template']->show('post/add');
			}				
		}
		else
		{
			$this->registry['template']->show('post/add');
		}
	}

}

?>