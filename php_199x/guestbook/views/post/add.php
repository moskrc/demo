<?php if (isset($errors) && !empty($errors)): ?>
	<h3>Исправьте ошибки</h3>
<?php endif ?>

<form action="/post/add" id="post_form" enctype="multipart/form-data" method="post">
<table>
<tr>
<td>
	Имя:
</td>
<td>
	<input type='text' name="data[Post][name]" size=30 maxlength=100 value="<?php if(isset($Post['name'])) echo $Post['name'] ?>">
	<div class="error"><?php if(isset($errors['Post']['name'])) echo $errors['Post']['name'] ?></div>
</td>
</tr>

<tr>
	<td>
		Email:
	</td>
	<td>
		<input type='text' name="data[Post][email]" size=30 maxlength=100 value="<?php if(isset($Post['email']))  echo $Post['email'] ?>">
		<div class="error"><?php if(isset($errors['Post']['email'])) echo $errors['Post']['email'] ?></div>
	</td>
</tr>

<tr>
	<td>
		Сообщение:
	</td>
	<td>
		<textarea name="data[Post][message]" cols=40 rows=5><?php if(isset($Post['message'])) echo $Post['message'] ?></textarea>
		<div class="error"><?php if(isset($errors['Post']['message'])) echo $errors['Post']['message'] ?></div>
	</td>
</tr>

<tr>
	<td>
		Картинка:
	</td>
	<td>
		<input name="userfile" type="file" />
		<div class="error"><?php if(isset($errors['Post']['userfile'])) echo $errors['Post']['userfile'] ?></div>
	</td>
</tr>

<tr>
	<td>&nbsp;</td>
	<td>	
		<input name='action' type='submit' value='Добавить сообщение'>
	</td>
</tr>


</table>
</form>

<br/>

<a href="/post/index">К списку постов</a>