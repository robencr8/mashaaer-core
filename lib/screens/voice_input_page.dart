
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import '../services/api_service.dart';

class VoiceInputPage extends StatefulWidget {
  @override
  _VoiceInputPageState createState() => _VoiceInputPageState();
}

class _VoiceInputPageState extends State<VoiceInputPage> {
  final recorder = Record();
  bool isRecording = false;
  String filePath = '/path/to/temp/audioFile.wav'; // Set appropriate path

  Future<void> _startRecording() async {
    if (await recorder.hasPermission()) {
      await recorder.start(path: filePath);
      setState(() {
        isRecording = true;
      });
    }
  }

  Future<void> _stopRecordingAndSubmit() async {
    final path = await recorder.stop();
    setState(() {
      isRecording = false;
    });
    if (path != null) {
      await ApiService().submitVoiceCommand(File(path));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Voice Command')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(isRecording ? 'Recording...' : 'Press to Record'),
            ElevatedButton(
              onPressed: isRecording ? _stopRecordingAndSubmit : _startRecording,
              child: Icon(isRecording ? Icons.stop : Icons.mic),
            )
          ],
        ),
      ),
    );
  }
}

