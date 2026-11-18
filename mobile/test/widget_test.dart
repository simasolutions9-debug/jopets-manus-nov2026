import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jopets/main.dart';

void main() {
  testWidgets('Jopets inicia el flujo de autenticación', (tester) async {
    await tester.pumpWidget(const JopetsApp());
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
