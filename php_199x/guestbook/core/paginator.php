<?php
class Paginator {

	var $page_size = PAGE_SIZE;
	var $link_padding = PAGE_LINK_PADDING;
	var $page_link_separator = PAGE_LINK_SEPARATOR;
	var $next_page_text = PAGE_NEXT_TEXT;
	var $prev_page_text = PAGE_PREV_TEXT;
	var $result_text_pattern = PAGES_STAT_STR;
	var $page_var = 'page';

	var $model;
	var $function;
	var $limitStr;
	var $total_rows;
	var $total_pages;
	var $cur_page;

	public function __construct($model,$function='getAll')
	{
		$this->model = $model;
		$this->function = $function;
		$this->cur_page = isset($_GET[$this->page_var]) && (int)$_GET[$this->page_var] > 0 ? (int)$_GET[$this->page_var] : 1;
	}

	public function getPages()
	{
		$r = call_user_func(array($this->model, $this->function),$this->query_paging());

		$this->total_rows = $this->model->getTotalRows();

		if ($this->page_size !== 0)
		$this->total_pages = ceil($this->total_rows/$this->page_size);

		return $r;
	}

	public function get_result_text()
	{
		$start = (($this->cur_page-1) * $this->page_size)+1;
		$end = (($start-1+$this->page_size) >= $this->total_rows)? $this->total_rows:($start-1+$this->page_size);

		if ($this->total_pages==0) $start = 0;
		
		return sprintf($this->result_text_pattern, $start, $end, $this->total_rows);
	}

	public function get_page_links()
	{
		if ( !isset($this->total_pages) ) return '';

		$page_link_list = array();

		$start = $this->cur_page - $this->link_padding;
		if ( $start < 1 ) $start = 1;
		$end = $this->cur_page + $this->link_padding-1;
		if ( $end > $this->total_pages ) $end = $this->total_pages;

		if ( $start > 1 )  $page_link_list[] = $this->get_page_link( $start-1, $start - 2 > 0 ? '...' : '' );
		for ($i=$start; $i <= $end; $i++)  $page_link_list[] = $this->get_page_link( $i );
		if ( $end + 1 < $this->total_pages ) $page_link_list[] = $this->get_page_link( $end +1, $end + 2 == $this->total_pages ? '' : '...' );
		if ( $end + 1 <= $this->total_pages ) $page_link_list[] = $this->get_page_link( $this->total_pages );

		return implode($this->page_link_separator, $page_link_list);
	}

	public function get_next_page_link()
	{
		return isset($this->total_pages) && $this->cur_page < $this->total_pages ? $this->get_page_link( $this->cur_page + 1, $this->next_page_text ) : '<span class="disabled_link">'.$this->next_page_text.'</span>';
	}

	public function get_prev_page_link()
	{
		return isset($this->total_pages) && $this->cur_page > 1 ? $this->get_page_link( $this->cur_page - 1, $this->prev_page_text ) : '<span class="disabled_link">'.$this->prev_page_text.'</span>';
	}

	private function get_page_link($page, $text='')
	{
		if (!$text) $text = $page;

		if ($page != $this->cur_page)
		{
			$url = '?'.$this->page_var.'='.$page;
			return '<a href="'.$url.'">'.$text.'</a>';
		}
		return '<span class="active_link">'.$text.'</span>';
	}

	private function query_paging()
	{
		if ($this->page_size != 0)
		{
			$start = ($this->cur_page-1) * $this->page_size;
			$res = "LIMIT {$start},{$this->page_size}";
		}
		return $res;
	}
}
?>