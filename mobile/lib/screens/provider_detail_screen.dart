import 'package:flutter/material.dart';
import '../api.dart';
import 'booking_screen.dart';
import 'marketplace_models.dart';

class ProviderDetailScreen extends StatefulWidget {
  const ProviderDetailScreen({super.key, required this.productId});
  final String productId;
  @override
  State<ProviderDetailScreen> createState() => _ProviderDetailScreenState();
}

class _ProviderDetailScreenState extends State<ProviderDetailScreen> {
  final api = JopetsApi();
  MarketplaceProvider? product;
  String? error;
  @override
  void initState() { super.initState(); load(); }
  Future<void> load() async { try { final row = await api.marketplaceProduct(widget.productId); if (mounted) setState(() => product = MarketplaceProvider.fromApi(row)); } catch (e) { if (mounted) setState(() => error = e.toString()); } }
  @override
  Widget build(BuildContext context) {
    final item = product;
    if (error != null) return Scaffold(appBar: AppBar(title: const Text('Servicio')), body: Center(child: Text(error!)));
    if (item == null) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    return Scaffold(
      appBar: AppBar(title: Text(item.name)),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Icon(Icons.business, size: 90),
          Text(item.name, style: Theme.of(context).textTheme.headlineSmall),
          Text('${item.price} ${item.currency}'),
          const Spacer(),
          SizedBox(width: double.infinity, child: FilledButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => BookingScreen(productId: item.id))), child: const Text('Reservar'))),
        ]),
      ),
    );
  }
}
