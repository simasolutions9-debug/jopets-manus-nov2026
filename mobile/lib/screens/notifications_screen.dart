import 'package:flutter/material.dart';
import '../api.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});
  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final api = JopetsApi();
  List<Map<String, dynamic>> rows = [];
  String? error;
  bool loading = true;
  @override
  void initState() { super.initState(); load(); }
  Future<void> load() async {
    setState(() { loading = true; error = null; });
    try {
      final value = await api.notifications();
      if (mounted) setState(() => rows = value);
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }
  @override
  Widget build(BuildContext context) {
    Widget body;
    if (loading) {
      body = const Center(child: CircularProgressIndicator());
    } else if (error != null) {
      body = Center(child: Column(mainAxisSize: MainAxisSize.min, children: [Text(error!, textAlign: TextAlign.center), OutlinedButton(onPressed: load, child: const Text('Reintentar'))]));
    } else if (rows.isEmpty) {
      body = const Center(child: Text('El servidor no devolvió notificaciones.'));
    } else {
      body = ListView.builder(itemCount: rows.length, itemBuilder: (_, index) { final row = rows[index]; return ListTile(leading: const Icon(Icons.notifications_outlined), title: Text(row['title']?.toString() ?? row['message']?.toString() ?? ''), subtitle: Text(row['created_at']?.toString() ?? '')); });
    }
    return Scaffold(appBar: AppBar(title: const Text('Notificaciones'), actions: [IconButton(onPressed: load, icon: const Icon(Icons.refresh))]), body: body);
  }
}
