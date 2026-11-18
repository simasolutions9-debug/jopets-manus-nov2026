import 'package:flutter/material.dart';

class MarketplaceProvider {
  const MarketplaceProvider({required this.id, required this.name, required this.price, required this.currency});
  final String id;
  final String name;
  final String price;
  final String currency;
  factory MarketplaceProvider.fromApi(Map<String, dynamic> row) {
    final id = row['id']?.toString();
    final name = row['name']?.toString();
    final price = row['price']?.toString();
    final currency = row['currency']?.toString();
    if (id == null || name == null || price == null || currency == null) throw const FormatException('Producto incompleto recibido del servidor');
    return MarketplaceProvider(id: id, name: name, price: price, currency: currency);
  }
  IconData get icon => Icons.business_center_rounded;
}
