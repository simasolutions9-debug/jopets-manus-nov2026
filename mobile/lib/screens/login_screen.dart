import 'package:flutter/material.dart';
import '../api.dart';
import '../main.dart';
import 'dashboard_screen.dart';
import 'provider_dashboard_screen.dart';
import 'register_screen.dart';

enum AccountRole { owner, provider, admin }

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, this.initialRole = AccountRole.owner});
  final AccountRole initialRole;
  @override State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  late AccountRole role;
  final email = TextEditingController();
  final password = TextEditingController();
  final totp = TextEditingController();
  bool loading = false;
  String? error;
  @override void initState() { super.initState(); role = widget.initialRole; }
  @override void dispose() { email.dispose(); password.dispose(); totp.dispose(); super.dispose(); }
  Future<void> submit() async {
    setState(() { loading = true; error = null; });
    try {
      final session = await JopetsApi().login(email: email.text.trim(), password: password.text, totpCode: totp.text.trim().isEmpty ? null : totp.text.trim());
      if (!mounted) return;
      final destination = session.role == 'proveedor' ? const ProviderDashboardScreen() : const DashboardScreen();
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => destination));
    } catch (e) { if (mounted) setState(() => error = e.toString()); }
    finally { if (mounted) setState(() => loading = false); }
  }
  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(backgroundColor: navy, foregroundColor: Colors.white, title: const Text('Iniciar sesión')),
        body: ListView(padding: const EdgeInsets.all(22), children: [
          const CircleAvatar(radius: 42, backgroundColor: navy, child: Icon(Icons.pets, size: 48, color: Colors.white)),
          const SizedBox(height: 12),
          const Center(child: Text('JOPETS', style: TextStyle(color: navy, fontSize: 28, fontWeight: FontWeight.w800, letterSpacing: 1.5))),
          const SizedBox(height: 20),
          SegmentedButton<AccountRole>(segments: const [ButtonSegment(value: AccountRole.owner, label: Text('Dueño'), icon: Icon(Icons.pets)), ButtonSegment(value: AccountRole.provider, label: Text('Proveedor'), icon: Icon(Icons.medical_services)), ButtonSegment(value: AccountRole.admin, label: Text('Admin'), icon: Icon(Icons.admin_panel_settings))], selected: {role}, onSelectionChanged: (value) => setState(() => role = value.first)),
          const SizedBox(height: 20),
          TextField(controller: email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Correo electrónico', border: OutlineInputBorder())),
          const SizedBox(height: 12),
          TextField(controller: password, obscureText: true, decoration: const InputDecoration(labelText: 'Contraseña', border: OutlineInputBorder())),
          const SizedBox(height: 12),
          TextField(controller: totp, decoration: const InputDecoration(labelText: 'Código MFA si es requerido', border: OutlineInputBorder())),
          if (error != null) Padding(padding: const EdgeInsets.symmetric(vertical: 12), child: Text(error!, style: const TextStyle(color: Colors.red))),
          const SizedBox(height: 12),
          SizedBox(width: double.infinity, child: FilledButton(onPressed: loading ? null : submit, child: Text(loading ? 'Conectando…' : 'Iniciar sesión'))),
          TextButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RegisterScreen())), child: const Text('Crear cuenta')),
        ],
      );
}
