
```dart
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class EmotionTimelinePage extends StatefulWidget {
  @override
  _EmotionTimelinePageState createState() => _EmotionTimelinePageState();
}

class _EmotionTimelinePageState extends State<EmotionTimelinePage> {
  Map<String, dynamic> _emotionData = {};

  @override
  void initState() {
    super.initState();
    _loadEmotionTimeline();
  }

  void _loadEmotionTimeline() async {
    try {
      var data = await ApiService().fetchEmotionTimeline();
      setState(() {
        _emotionData = data;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading emotion data: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Emotion Timeline'),
      ),
      body: _emotionData.isEmpty
          ? Center(child: CircularProgressIndicator())
          : ListView(
              children: _emotionData.entries.map((entry) {
                return ListTile(
                  title: Text(entry.key),
                  subtitle: Text('Count: ${entry.value}'),
                );
              }).toList(),
            ),
    );
  }
}
```
