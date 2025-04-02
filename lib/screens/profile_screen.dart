
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  final String userName;
  ProfileScreen({required this.userName});

  @override
  _ProfileScreenState createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic> _userProfile = {};

  @override
  void initState() {
    super.initState();
    _loadUserProfile();
  }

  void _loadUserProfile() async {
    try {
      var profile = await ApiService().fetchUserProfile(widget.userName);
      setState(() {
        _userProfile = profile;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading profile: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('User Profile')),
      body: _userProfile.isEmpty
          ? Center(child: CircularProgressIndicator())
          : ListView(
              children: _userProfile.entries.map((entry) {
                return ListTile(
                  title: Text(entry.key),
                  subtitle: Text(entry.value.toString()),
                );
              }).toList(),
            ),
    );
  }
}

