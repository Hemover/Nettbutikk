CREATE DATABASE IF NOT EXISTS nettbutikk
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

  USE nettbutikk;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image VARCHAR(255),
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, description, price, image, stock) VALUES
(
  'TP-LINK Wireless Router (TL-WR841N)',
  'En router som gir deg trådløs tilkobling med 300Mbps nedlastingshastighet',
  300,
  'image/TP-LINKwireless_ruter.avif',
  25
),
(
  'Cisco Meraki Mx67 Router Security Appliance',
  'Cisco Meraki MX67 Router Sikkerhetsapparat ...',
  4999,
  'image/firewall.jpg',
  15
),
(
  '24-Port Gigabit Smart Switch GS724TV6',
  'NETGEAR Gigabit Smart-switch med 24 porter...',
  2339,
  'image/switch.jpg',
  20
);

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES products(id)
);

