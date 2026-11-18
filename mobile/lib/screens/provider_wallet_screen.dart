import 'package:flutter/material.dart';
import '../api.dart';

class ProviderWalletScreen extends StatefulWidget {
  const ProviderWalletScreen({super.key});
  @override
  State<ProviderWalletScreen> createState() => _ProviderWalletScreenState();
}

class _ProviderWalletScreenState extends State<ProviderWalletScreen> {
  final api = JopetsApi();
  Map<String, dynamic>? wallet;
  String? error;
  bool loading = true;
  @override
  void initState() { super.initState(); load(); }
  Future<void> load() async {
    setState(() { loading = true; error = null; });
    try {
      final value = await api.providerWallet();
      if (mounted) setState(() => wallet = value);
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }
  @override
  Widget build(BuildContext context) {
    final data = wallet;
    if (loading) return Scaffold(appBar: AppBar(title: const Text('Billetera')), body: const Center(child: CircularProgressIndicator()));
    if (error != null) return Scaffold(appBar: AppBar(title: const Text('Billetera')), body: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [Text(error!, textAlign: TextAlign.center), OutlinedButton(onPressed: load, child: const Text('Reintentar'))])));
    if (data == null) return Scaffold(appBar: AppBar(title: const Text('Billetera')), body: const Center(child: Text('El servidor no devolvió la billetera.')));
    final transactions = (data['transactions'] as List?)?.whereType<Map>().toList() ?? <Map>[];
    return Scaffold(appBar: AppBar(title: const Text('Billetera'), actions: [IconButton(onPressed: load, icon: const Icon(Icons.refresh))]), body: ListView(padding: const EdgeInsets.all(20), children: [Card(child: ListTile(title: const Text('Saldo disponible'), subtitle: Text(data['balance']?.toString() ?? ''), trailing: Text(data['currency']?.toString() ?? ''))), const SizedBox(height: 16), const Text('Transacciones'), ...transactions.map((row) => ListTile(leading: const Icon(Icons.receipt_long), title: Text(row['description']?.toString() ?? ''), trailing: Text(row['amount']?.toString() ?? '')))]));
  }
}
