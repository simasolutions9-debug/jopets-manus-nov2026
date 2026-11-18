import 'package:flutter/material.dart';
import 'api.dart';
import 'screens/dashboard_screen.dart';
import 'screens/login_screen.dart';
import 'screens/provider_dashboard_screen.dart';

const navy = Color(0xFF073B78);
const orange = Color(0xFFFF651F);

void main() => runApp(const JopetsApp());

class JopetsApp extends StatelessWidget {
  const JopetsApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Jopets',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(useMaterial3: true, colorSchemeSeed: orange, scaffoldBackgroundColor: const Color(0xFFF7F8FA)),
        home: const LaunchScreen(),
      );
}

class LaunchScreen extends StatefulWidget {
  const LaunchScreen({super.key});
  @override State<LaunchScreen> createState() => _LaunchScreenState();
}

class _LaunchScreenState extends State<LaunchScreen> {
  @override void initState() { super.initState(); _restore(); }
  Future<void> _restore() async {
    final api = JopetsApi();
    if (!await api.hasStoredSession()) return;
    final role = await api.role();
    if (!mounted) return;
    Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => role == 'proveedor' ? const ProviderDashboardScreen() : const DashboardScreen()));
  }
  @override
  Widget build(BuildContext context) => Scaffold(
        body: DecoratedBox(
          decoration: const BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [navy, Color(0xFF021B3A)])),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(children: [
                const Spacer(),
                const CircleAvatar(radius: 54, backgroundColor: Colors.white, child: Icon(Icons.pets, size: 64, color: orange)),
                const SizedBox(height: 16),
                const Text('JOPETS', style: TextStyle(color: Colors.white, fontSize: 38, fontWeight: FontWeight.w800, letterSpacing: 2)),
                const Text('Cuidado que se siente', style: TextStyle(color: Colors.white70, fontSize: 16)),
                const Spacer(),
                _LaunchButton(label: 'SOY DUEÑO DE MASCOTA', onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const LoginScreen(initialRole: AccountRole.owner)))),
                const SizedBox(height: 14),
                const Text('¿Eres proveedor de servicios?', style: TextStyle(color: Colors.white)),
                TextButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const LoginScreen(initialRole: AccountRole.provider))), child: const Text('Iniciar como proveedor', style: TextStyle(color: orange))),
                TextButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const LoginScreen(initialRole: AccountRole.admin))), child: const Text('Iniciar sesión', style: TextStyle(color: Colors.white))),
                const SizedBox(height: 16),
                const Text('© 2026 Jopets®', style: TextStyle(color: Colors.white54, fontSize: 10)),
              ]),
            ),
          ),
        ),
      );
}

class _LaunchButton extends StatelessWidget {
  const _LaunchButton({required this.label, required this.onTap});
  final String label;
  final VoidCallback onTap;
  @override Widget build(BuildContext context) => SizedBox(width: double.infinity, child: FilledButton(onPressed: onTap, style: FilledButton.styleFrom(backgroundColor: Colors.white, foregroundColor: orange, padding: const EdgeInsets.symmetric(vertical: 18)), child: Text(label)));
}
