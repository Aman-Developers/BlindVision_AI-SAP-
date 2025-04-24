import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:object_detection_app/main.dart';

void main() {
  testWidgets('Object Detection App navigation test', (WidgetTester tester) async {
    // Load the app
    await tester.pumpWidget(ObjectDetectionApp());

    // Verify the home screen shows welcome text
    expect(find.text('Welcome back!'), findsOneWidget);

    // Tap on the Detect icon in bottom navigation
    await tester.tap(find.byIcon(Icons.camera_alt));
    await tester.pumpAndSettle();

    // Verify that the camera preview or loading indicator is present
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
