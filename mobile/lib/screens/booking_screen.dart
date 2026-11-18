import 'package:flutter/material.dart';
import '../api.dart';
import 'marketplace_models.dart';

class BookingScreen extends StatefulWidget {
  const BookingScreen({super.key, required this.productId});
  final String productId;
  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  final api = JopetsApi();
  MarketplaceProvider? product;
  bool loading = true;
  String? error;
  @override
  void initState() { super.initState(); load(); }
  Future<void> load() async {
    try { product = MarketplaceProvider.fromApi(await api.marketplaceProduct(widget.productId)); if (mounted) setState(() => loading = false); }
    catch (e) { if (mounted) setState(() { error = e.toString(); loading = false; }); }
  }
  Future<void> confirm() async {
    final item = product;
    if (item == null) return;
    setState(() => loading = true);
    try { final pets = await api.pets(); if (pets.isEmpty) throw const ApiException(422, 'El servidor no devolvió mascotas para reservar.'); await api.createBooking(pets.first['id'].toString(), {'product_id': item.id, 'price': item.price, 'currency': item.currency}); if (mounted) Navigator.pop(context); }
    catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString()))); }
    finally { if (mounted) setState(() => loading = false); }
  }
  @override
  Widget build(BuildContext context) {
    final item = product;
    return Scaffold(
      appBar: AppBar(title: const Text('Reserva')),
      body: error != null ? Center(child: Text(error!)) : item == null ? const Center(child: CircularProgressIndicator()) : Padding(padding: const EdgeInsets.all(20), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(item.name, style: Theme.of(context).textTheme.headlineSmall), Text('${item.price} ${item.currency}'), const SizedBox(height: 12), const Text('La confirmación se enviará al servidor Django.'), const Spacer(), SizedBox(width: double.infinity, child: FilledButton(onPressed: loading ? null : confirm, child: Text(loading ? 'Enviando…' : 'Confirmar reserva')))])),
    );
  }
}
