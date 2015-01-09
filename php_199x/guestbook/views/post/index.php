
<a href="/post/add">Добавить запись</a>

<div id="posts">

<?php if(empty($posts)): ?>
<p>В БД записей не обнаружено. <a href="/post/add">Будь первым!</a></p>
<?php endif ?>

<?php foreach($posts as $post): ?>
<div class="post">
	<div class="post_text_part">
		<div class="post_top_line">
			<span class="id">#&nbsp;<?php echo ($post['id']) ?></span>
			
			<span class="email">Email:&nbsp;<a href="mailto:<?php echo ($post['email']) ?>"><?php echo ($post['email']) ?></a></span>
		
			<span class="created_at">Добавлено:&nbsp;<?php echo ($post['created_at']) ?></span>
		</div>
		
		<div class="name"><?php echo ($post['name']) ?></div>
		
		<?php if (file_exists(SITE_PATH.'/images'.DIRSEP.'uploaded'.DIRSEP.$post['id'].'.jpg')): ?>
		<div class="post_image_part">
			<img src="<?php echo '/images'.DIRSEP.'uploaded'.DIRSEP.$post['id'].'.jpg' ?>" alt="logo"/>
		</div>
		<?php endif; ?>
		<p><?php echo ($post['message']) ?>
		
		</p>
	</div>
</div>
<?php endforeach; ?>

</div>

<div id="paginator">
	<div id="statistic">
		<?php echo $paginator->get_result_text().' записей'; ?>
	</div>
	<div id="pages">
		<?php echo 'Страницы: '.$paginator->get_prev_page_link().$paginator->get_page_links().$paginator->get_next_page_link(); ?>
	</div>
</div>
