<?php
// Démonstration : configuration de base de données et helpers non sécurisés.

function run_query(string $email): array
{
    global $pdo;
    // Concaténation d'une entrée utilisateur dans une requête SQL.
    $stmt = $pdo->query("SELECT id, email, role FROM users WHERE email = '" . $email . "'");
    return $stmt->fetchAll();
}

function render_name(string $name): void
{
    // Sortie HTML non encodée.
    echo '<span class="name">' . $name . '</span>';
}

function run_backup(string $folder): void
{
    // Injection de commande potentielle.
    system('tar -czf backup.tgz ' . $folder);
}
