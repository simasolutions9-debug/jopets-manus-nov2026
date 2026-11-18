import 'package:flutter/material.dart';
import '../api.dart';

const _navy = Color(0xFF123B73);

class BookingsListScreen extends StatefulWidget {
  const BookingsListScreen({super.key});
  @override
  State<BookingsListScreen> createState() => _BookingsListScreenState();
}

class _BookingsListScreenState extends State<BookingsListScreen> with SingleTickerProviderStateMixin {
  late final TabController tabs = TabController(length: 2, vsync: this);
  final api = JopetsApi();
  List<Map<String, dynamic>> rows = [];
  String? error;
  bool loading = true;
  @override
  void initState() { super.initState(); load(); }
  @override
  void dispose() { tabs.dispose(); super.dispose(); }
  Future<void> load() async {
    setState(() { loading = true; error = null; });
    try { final value = await api.bookings(); if (mounted) setState(() => rows = value); }
    catch (e) { if (mounted) setState(() => error = e.toString()); }
    finally { if (mounted) setState(() => loading = false); }
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(backgroundColor: _navy, foregroundColor: Colors.white, title: const Text('Reservas'), actions: [IconButton(onPressed: load, icon: const Icon(Icons.refresh))], bottom: TabBar(controller: tabs, tabs: const [Tab(text: 'Próximas'), Tab(text: 'Pasadas')])),
      body: loading ? const Center(child: CircularProgressIndicator()) : error != null ? Center(child: Text(error!)) : TabBarView(controller: tabs, children: [_BookingList(rows: rows, past: false), _BookingList(rows: rows, past: true)]),
    );
  }
}

class _BookingList extends StatelessWidget {
  const _BookingList({required this.rows, required this.past});
  final List<Map<String, dynamic>> rows;
  final bool past;
  @override
  Widget build(BuildContext context) {
    final filtered = rows.where((row) { final state = row['state']?.toString(); return past ? state == 'completed' || state == 'cancelled' : state != 'completed' && state != 'cancelled'; }).toList();
    if (filtered.isEmpty) return Center(child: Text(past ? 'El servidor no devolvió reservas pasadas.' : 'El servidor no devolvió reservas próximas.'));
    return ListView.builder(padding: const EdgeInsets.all(16), itemCount: filtered.length, itemBuilder: (_, index) {
      final row = filtered[index];
      final snapshot = row['price_snapshot'] is Map ? row['price_snapshot'] as Map : const {};
      return Card(child: ListTile(leading: const Icon(Icons.event), title: Text(row['id']?.toString() ?? ''), subtitle: Text('${row['state'] ?? ''} • Mascota ${row['pet_id'] ?? ''}'), trailing: Text(snapshot['price']?.toString() ?? '')));
    });
  }
}
