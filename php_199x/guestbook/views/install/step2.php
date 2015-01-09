<script type="text/javascript">
function checkInput(form) {
	if (form.login.value.length < 3) {
		alert("Логин должен быть не короче 3-х символов");
		return false;
	}
	
	if (form.passwd.value.length < 1) {
		alert("Введите пароль");
		return false;
	}
	
	if (form.passwd.value != form.passwd2.value) {
		alert("Пароли не совпадают");
		return false;
	}

	return true;
}
</script>

<div id="install">

<form action="/install/step2do" method="post" id="install_form" onsubmit="return checkInput(this);">
<table>
<tr>
	<td>
		<label for="username">Логин:</label>
	</td>
	<td>
		<input type="text" name="data[Install][login]" id="login" value="<?php if(isset($Install['login'])) echo $Install['login'] ?>"/>
	</td>
</tr>

<tr>
	<td>
		<label for="email">Email:</label>
	</td>
	<td>
		<input type="text" name="data[Install][email]" id="email" value="<?php if(isset($Install['email'])) echo $Install['email'] ?>"/>
	</td>
</tr>


<tr>
	<td>
		<label for="username">Пароль:</label>
	</td>
	<td>
		<input type="password" name="data[Install][passwd]" id="passwd" value="<?php if(isset($Install['passwd'])) echo $Install['passwd'] ?>"/>
	</td>
</tr>

<tr>
	<td>
		<label for="username">Пароль еще раз:</label>
	</td>
	<td>
		<input type="password" name="data[Install][passwd2]" id="passwd2" value="<?php if(isset($Install['passwd2'])) echo $Install['passwd2'] ?>"/>
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

<p>Детальное конфигурирование в администраторском разделе</p>
<br/>
</div>
