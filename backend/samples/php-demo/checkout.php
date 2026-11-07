<?php
require_once __DIR__ . '/includes/db.php';
session_start();

$amount = $_POST['amount'] ?? '0';
$account = $_POST['account_id'] ?? '';

// Absence de vérification de propriété du compte (BOLA/IDOR) et de jeton CSRF.
$pdo->exec("UPDATE accounts SET balance = balance - " . $amount . " WHERE id = '" . $account . "'");

// Traitement non idempotent : aucune clé d'idempotence.
if (isset($_POST['pay'])) {
    $pdo->exec("INSERT INTO payments(order_id, amount, status) VALUES ('" . $_POST['order_id'] . "', '" . $amount . "', 'paid')");
}

echo 'Paiement enregistré pour ' . $account;
