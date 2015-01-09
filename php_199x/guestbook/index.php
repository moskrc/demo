<?php
# Константы
require 'core/startup.php';

# Создание реестра
$registry = new Registry;

# Загрузка и регистрация шаблона
$template = new Template($registry);
$registry->set ('template', $template);

# Загрузка, настройка и регистрация роутера
$router = new Router($registry);
$registry->set ('router', $router);
$router->setPath (SITE_PATH . 'controllers');

# Старт
$router->delegate();

?>
