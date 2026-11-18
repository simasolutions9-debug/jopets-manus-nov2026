import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _Slide {
  const _Slide(this.title, this.description, this.icon);
  final String title;
  final String description;
  final IconData icon;
}

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key, required this.home});
  final Widget home;
  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final controller = PageController();
  int page = 0;
  final slides = const <_Slide>[
    _Slide('Encuentra servicios de confianza', 'Conecta con paseadores y veterinarios.', Icons.handshake),
    _Slide('Reserva y paga seguro', 'Gestiona todo desde la app.', Icons.lock),
    _Slide('Sigue el paseo en tiempo real', 'Recibe actualizaciones al instante.', Icons.location_on),
  ];
  @override
  void dispose() { controller.dispose(); super.dispose(); }
  Future<void> finish() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('onboarding_seen', true);
    if (mounted) Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => homeWidget()));
  }
  Widget homeWidget() => widget.home;
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Align(alignment: Alignment.centerRight, child: TextButton(onPressed: finish, child: const Text('Saltar'))),
            Expanded(child: PageView.builder(controller: controller, itemCount: slides.length, onPageChanged: (value) => setState(() => page = value), itemBuilder: (context, index) {
              final slide = slides[index];
              return Column(mainAxisAlignment: MainAxisAlignment.center, children: [CircleAvatar(radius: 100, child: Icon(slide.icon, size: 80)), const SizedBox(height: 28), Text(slide.title, textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall), Padding(padding: const EdgeInsets.all(24), child: Text(slide.description, textAlign: TextAlign.center))]);
            })),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: List.generate(slides.length, (index) => Padding(padding: const EdgeInsets.all(4), child: CircleAvatar(radius: 5, backgroundColor: index == page ? Colors.orange : Colors.grey)))),
            Padding(padding: const EdgeInsets.all(24), child: SizedBox(width: double.infinity, child: FilledButton(onPressed: page == slides.length - 1 ? finish : () => controller.nextPage(duration: const Duration(milliseconds: 250), curve: Curves.easeOut), child: Text(page == slides.length - 1 ? 'Comenzar' : 'Continuar')))),
          ],
        ),
      ),
    );
  }
}
