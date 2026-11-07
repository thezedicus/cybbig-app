<?php
/**
 * PROJET DE DÉMONSTRATION CYBBIG — VOLONTAIREMENT VULNÉRABLE.
 * Ne pas déployer. Sert uniquement à tester le scanner statique local.
 */
session_start();

$pdo = new PDO('mysql:host=localhost;dbname=demo', 'demo', 'demo_password_123');
$search = $_GET['q'] ?? '';

// SQL injection : concaténation directe d'une entrée utilisateur.
$sql = "SELECT * FROM products WHERE name LIKE '%" . $search . "%'";
$rows = $pdo->query($sql);

// XSS : sortie non encodée.
echo "<h1>Résultats pour " . $search . "</h1>";

// Inclusion dynamique.
$page = $_GET['page'] ?? 'home';
include __DIR__ . '/pages/' . $page . '.php';

// Secret en clair (fictif).
$stripe_secret = "sk_test_DEMO_FAKE_cybbig_not_a_real_key";

// Téléversement sans contrôle réel.
if (!empty($_FILES['receipt'])) {
    move_uploaded_file($_FILES['receipt']['tmp_name'], __DIR__ . '/uploads/' . $_FILES['receipt']['name']);
}

// Session non régénérée après authentification.
if (isset($_POST['login'])) {
    $_SESSION['user'] = $_POST['email'];
}

// Comparaison faible.
if (isset($_GET['token']) && $_GET['token'] == 'demo-token') {
    echo 'ok';
}
