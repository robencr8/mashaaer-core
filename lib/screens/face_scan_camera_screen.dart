
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

class FaceScanCameraScreen extends StatefulWidget {
  @override
  _FaceScanCameraScreenState createState() => _FaceScanCameraScreenState();
}

class _FaceScanCameraScreenState extends State<FaceScanCameraScreen> {
  final picker = ImagePicker();

  Future<void> _getImageAndSubmit() async {
    final pickedFile = await picker.getImage(source: ImageSource.camera);
    
    if (pickedFile != null) {
      try {
        await ApiService().submitFaceImage(File(pickedFile.path));
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Image submitted successfully')));
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error submitting face image: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Face Recognition')),
      body: Center(
        child: ElevatedButton(
          onPressed: _getImageAndSubmit,
          child: Text('Capture Image'),
        ),
      ),
    );
  }
}

