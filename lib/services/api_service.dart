import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = 'http://0.0.0.0:5000/api';

  Future<Map<String, dynamic>> fetchEmotionTimeline() async {
    // Existing fetchEmotionTimeline() code  (This needs to be implemented separately)
    try {
      final response = await http.get(Uri.parse('$baseUrl/timeline'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to fetch emotion timeline');
      }
    } catch (e) {
      throw Exception('Error fetching emotion timeline: $e');
    }
  }

  Future<String> submitVoiceCommand(File audioFile) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/listen'));
      request.files.add(await http.MultipartFile.fromPath('audio', audioFile.path));
      var response = await request.send();

      if (response.statusCode == 200) {
        var responseData = await http.Response.fromStream(response);
        return jsonDecode(responseData.body);
      }
      throw Exception('Failed to submit voice command');
    } catch (e) {
      throw Exception('Error submitting voice command: $e');
    }
  }

  Future<Map<String, dynamic>> fetchUserProfile(String name) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/profile/$name'));
      if (response.statusCode == 200) return jsonDecode(response.body);
      throw Exception('Failed to load user profile');
    } catch (e) {
      throw Exception('Error fetching user profile: $e');
    }
  }

  Future<String> submitFaceImage(File imageFile) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/detect-face'));
      request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
      var response = await request.send();

      if (response.statusCode == 200) {
        var responseData = await http.Response.fromStream(response);
        return jsonDecode(responseData.body);
      }
      throw Exception('Failed to submit face image');
    } catch (e) {
      throw Exception('Error submitting face image: $e');
    }
  }
}