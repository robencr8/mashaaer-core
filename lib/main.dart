// lib/screens/emotion_timeline_page.dart
import 'package:flutter/material.dart';
import '../services/api_service.dart'; // Assuming api_service.dart is in services folder

class EmotionTimelinePage extends StatefulWidget {
  const EmotionTimelinePage({Key? key}) : super(key: key);

  @override
  State<EmotionTimelinePage> createState() => _EmotionTimelinePageState();
}

class _EmotionTimelinePageState extends State<EmotionTimelinePage> {
  List emotionLogs = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchEmotionLogs();
  }

  Future<void> _fetchEmotionLogs() async {
    try {
      final logs = await ApiService.fetchEmotionLogs();
      setState(() {
        emotionLogs = logs;
        isLoading = false;
      });
    } catch (e) {
      // Handle error appropriately
      print('Error fetching emotion logs: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Emotion Timeline')),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: emotionLogs.length,
              itemBuilder: (context, index) {
                final log = emotionLogs[index];
                return ListTile(
                  title: Text('Emotion: ${log['emotion']}'), // Adjust based on your API response
                  subtitle: Text('Timestamp: ${log['timestamp']}'), // Adjust based on your API response
                );
              },
            ),
    );
  }
}


// lib/main.dart (or home_page.dart, assuming this is where navigation is handled)
import 'package:flutter/material.dart';
import 'screens/emotion_timeline_page.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: Center(
        child: ElevatedButton(
          child: const Text('Go to Emotion Timeline'),
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => EmotionTimelinePage()),
            );
          },
        ),
      ),
    );
  }
}