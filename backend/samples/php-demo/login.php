<?php
require_once __DIR__ . '/includes/db.php';
session_start();

$email = $_POST['email'] ?? '';
$password = $_POST['password'] ?? '';

// Concaténation SQL + comparaison non stricte.
$user = $pdo->query("SELECT * FROM users WHERE email = '" . $email . "'")->fetch();

if ($user && md5($password) === $user['password']) {
    $_SESSION['user_id'] = $user['id'];
    // Pas de session_regenerate_id(true) après authentification.
    header('Location: /account.php');
    exit;
}

// Comparaison faible pouvant accepter des valeurs inattendues.
if (isset($_GET['debug']) && $_GET['debug'] == '1') {
    var_dump($user);
}

echo '<form method="post">' .
     '<input name="email" value="' . $email . '">' .
     '<input name="password" type="password">' .
     '<button>Connexion</button></form>';
