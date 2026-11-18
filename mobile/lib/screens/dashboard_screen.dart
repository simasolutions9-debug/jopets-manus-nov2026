import 'package:flutter/material.dart';
import '../api.dart';
import '../main.dart';
import 'bookings_list_screen.dart';
import 'chat_screen.dart';
import 'marketplace_screen.dart';
import 'medical_history_screen.dart';
import 'pet_profile_edit_screen.dart';
import 'pet_qr_screen.dart';
import 'settings_screen.dart';

class DashboardScreen extends StatefulWidget { const DashboardScreen({super.key}); @override State<DashboardScreen> createState() => _DashboardScreenState(); }
class _DashboardScreenState extends State<DashboardScreen> {
  final api = JopetsApi();
  List<Map<String, dynamic>> pets = [];
  String? error;
  @override void initState() { super.initState(); load(); }
  Future<void> load() async { try { final value = await api.pets(); if (mounted) setState(() { pets = value; error = null; }); } catch (e) { if (mounted) setState(() => error = e.toString()); } }
  Future<void> openChat() async {
    try {
      final tenantId = await api.tenantIdValue();
      final bookings = await api.bookings();
      String? peerId;
      for (final booking in bookings) { final value = booking['provider_id']?.toString(); if (value != null && value.isNotEmpty) { peerId = value; break; } }
      if (tenantId == null || tenantId.isEmpty || peerId == null) throw const ApiException(422, 'No existe una reserva con proveedor asignado para iniciar el chat.');
      if (!mounted) return;
      Navigator.push(context, MaterialPageRoute(builder: (_) => ChatScreen(tenantId: tenantId, peerId: peerId)));
    } catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString()))); }
  }
  @override Widget build(BuildContext context) {
    final pet = pets.isEmpty ? null : pets.first;
    return Scaffold(backgroundColor: const Color(0xFFF7F8FA), appBar: AppBar(backgroundColor: navy, foregroundColor: Colors.white, title: Text(pet?['name']?.toString() ?? 'Jopets'), actions: [IconButton(onPressed: load, icon: const Icon(Icons.refresh)), IconButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())), icon: const Icon(Icons.person_outline))]), body: error != null ? _Error(message: error!, retry: load) : pet == null ? const Center(child: Text('El servidor no devolvió mascotas.')) : ListView(padding: const EdgeInsets.all(16), children: [_PetHeader(pet: pet), const SizedBox(height: 14), Row(children: [Expanded(child: _ActionCard(icon: Icons.qr_code, label: 'Código QR', onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => PetQrScreen(petId: pet['id'].toString()))))), const SizedBox(width: 8), Expanded(child: _ActionCard(icon: Icons.medical_information, label: 'Salud', onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => MedicalHistoryScreen(petId: pet['id'].toString()))))), const SizedBox(width: 8), Expanded(child: _ActionCard(icon: Icons.edit, label: 'Perfil', onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => PetProfileEditScreen(petId: pet['id'].toString())))))]), const SizedBox(height: 14), _RouteCard(title: 'Servicios', icon: Icons.search, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const MarketplaceScreen()))), _RouteCard(title: 'Próximas citas', icon: Icons.calendar_month, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const BookingsListScreen()))) ]), bottomNavigationBar: NavigationBar(destinations: const [NavigationDestination(icon: Icon(Icons.home), label: 'Inicio'), NavigationDestination(icon: Icon(Icons.history), label: 'Historial'), NavigationDestination(icon: Icon(Icons.chat), label: 'Mensajes'), NavigationDestination(icon: Icon(Icons.person), label: 'Cuenta')], onDestinationSelected: (index) { if (index == 1) Navigator.push(context, MaterialPageRoute(builder: (_) => const BookingsListScreen())); if (index == 2) openChat(); if (index == 3) Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())); }));
  }
}
class _PetHeader extends StatelessWidget { const _PetHeader({required this.pet}); final Map<String, dynamic> pet; @override Widget build(BuildContext context) => Card(color: navy, child: ListTile(leading: const CircleAvatar(child: Icon(Icons.pets)), title: Text(pet['name']?.toString() ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)), subtitle: Text('${pet['species'] ?? ''} • ${pet['breed'] ?? ''}', style: const TextStyle(color: Colors.white70)))); }
class _ActionCard extends StatelessWidget { const _ActionCard({required this.icon, required this.label, required this.onTap}); final IconData icon; final String label; final VoidCallback onTap; @override Widget build(BuildContext context) => Card(child: InkWell(onTap: onTap, child: Padding(padding: const EdgeInsets.all(12), child: Column(children: [Icon(icon, color: orange), const SizedBox(height: 8), Text(label)])))); }
class _RouteCard extends StatelessWidget { const _RouteCard({required this.title, required this.icon, required this.onTap}); final String title; final IconData icon; final VoidCallback onTap; @override Widget build(BuildContext context) => Card(child: ListTile(onTap: onTap, leading: Icon(icon, color: orange), title: Text(title), trailing: const Icon(Icons.chevron_right))); }
class _Error extends StatelessWidget { const _Error({required this.message, required this.retry}); final String message; final VoidCallback retry; @override Widget build(BuildContext context) => Center(child: Column(mainAxisSize: MainAxisSize.min, children: [Text(message, textAlign: TextAlign.center), OutlinedButton(onPressed: retry, child: const Text('Reintentar'))])); }
