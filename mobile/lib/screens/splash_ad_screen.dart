import 'package:flutter/material.dart';
import '../api.dart';
import '../main.dart';

class SplashAdScreen extends StatefulWidget {
  const SplashAdScreen({super.key});
  @override
  State<SplashAdScreen> createState() => _SplashAdScreenState();
}
class _SplashAdScreenState extends State<SplashAdScreen> {
  @override
  void initState() { super.initState(); _route(); }
  Future<void> _route() async { final api = JopetsApi(); final session = await api.hasStoredSession(); final role = await api.role(); if (!mounted) return; Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => session ? AuthenticatedRouter(role: role) : const HomeScreen())); }
  @override
  Widget build(BuildContext context) => const Scaffold(body: Center(child: CircularProgressIndicator()));
}
