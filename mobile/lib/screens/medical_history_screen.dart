import 'package:flutter/material.dart';
import '../api.dart';

class MedicalHistoryScreen extends StatefulWidget {
  const MedicalHistoryScreen({super.key, required this.petId});
  final String petId;
  @override
  State<MedicalHistoryScreen> createState() => _MedicalHistoryScreenState();
}

class _MedicalHistoryScreenState extends State<MedicalHistoryScreen> {
  final api = JopetsApi();
  Map<String, dynamic>? data;
  String? error;
  @override
  void initState() { super.initState(); load(); }
  Future<void> load() async {
    try {
      final value = await api.medicalHistory(widget.petId);
      if (mounted) setState(() => data = value);
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    }
  }
  @override
  Widget build(BuildContext context) {
    if (error != null) return Scaffold(appBar: AppBar(title: const Text('Historial médico')), body: Center(child: Text(error!)));
    if (data == null) return Scaffold(appBar: AppBar(title: const Text('Historial médico')), body: const Center(child: CircularProgressIndicator()));
    final vaccines = (data!['vaccines'] as List?)?.whereType<Map>().toList() ?? <Map>[];
    final records = (data!['records'] as List?)?.whereType<Map>().toList() ?? <Map>[];
    final children = <Widget>[Text('Vacunas', style: Theme.of(context).textTheme.titleLarge)];
    children.addAll(vaccines.map((row) => ListTile(leading: const Icon(Icons.vaccines), title: Text(row['name']?.toString() ?? ''), subtitle: Text(row['administered_at']?.toString() ?? ''))));
    children.add(const SizedBox(height: 16));
    children.add(Text('Registros', style: Theme.of(context).textTheme.titleLarge));
    children.addAll(records.map((row) => ListTile(leading: const Icon(Icons.medical_information), title: Text(row['title']?.toString() ?? ''), subtitle: Text(row['occurred_at']?.toString() ?? ''))));
    if (vaccines.isEmpty && records.isEmpty) children.add(const Text('El servidor no devolvió registros médicos.'));
    return Scaffold(appBar: AppBar(title: const Text('Historial médico')), body: ListView(padding: const EdgeInsets.all(20), children: children));
  }
}
