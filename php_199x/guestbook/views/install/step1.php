<div id="install">

<form action="/install/step1do" method="post" id="install_form">
<table>
<tr>
	<td>
		<label for="host">Адрес сервера MySQL:</label>
	</td>
	<td>
		<input type="text" name="data[Install][host]" id="host" value="<?php if(isset($Install['host']))  echo $Install['host'] ?>"/>
	</td>
</tr>

<tr>
	<td>
		<label for="login">Логин:</label>
	</td>
	<td>
		<input type="text" name="data[Install][login]" id="login" value="<?php if(isset($Install['login']))  echo $Install['login'] ?>"/>
		
	</td>
</tr>



<tr>
	<td>
		<label for="passwd">Пароль:</label>
	</td>
	<td>
		<input type="password" name="data[Install][passwd]" id="passwd" value="<?php if(isset($Install['passwd']))  echo $Install['passwd'] ?>"/>
	</td>
</tr>



<tr>
	<td>
		<label for="db">Название БД:</label>
	</td>
	<td>
		<input type="text" name="data[Install][db]" id="db" value="<?php if(isset($Install['db']))  echo $Install['db'] ?>"/>
	</td>
</tr>

<tr>
	<td>
		&nbsp;
	</td>
	<td>
		<input name='action' type='submit' value='Далее'>
	</td>
</tr>
</table>
</form>


<br/>
<?php if (isset($errors)): ?>
	<p class="error">
		Возникла ошибка
	</p>
	<p>
		<?php echo $errors['Install'] ?>
	</p>
<?php endif; ?>
</div>
