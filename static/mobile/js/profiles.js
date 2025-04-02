document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const userStatus = document.getElementById('userStatus');
  const profilesContainer = document.getElementById('profilesContainer');
  const addProfileButton = document.getElementById('addProfileButton');
  const profileModal = document.getElementById('profileModal');
  const closeProfileModal = document.getElementById('closeProfileModal');
  const profileModalTitle = document.getElementById('profileModalTitle');
  const profileModalBody = document.getElementById('profileModalBody');
  const addProfileModal = document.getElementById('addProfileModal');
  const closeAddProfileModal = document.getElementById('closeAddProfileModal');
  const profileName = document.getElementById('profileName');
  const profilePhotoPreview = document.getElementById('profilePhotoPreview');
  const metadataKey = document.getElementById('metadataKey');
  const metadataValue = document.getElementById('metadataValue');
  const addMetadataButton = document.getElementById('addMetadataButton');
  const metadataList = document.getElementById('metadataList');
  const saveProfileButton = document.getElementById('saveProfileButton');
  const profileCameraView = document.getElementById('profileCameraView');
  const closeProfileCameraButton = document.getElementById('closeProfileCameraButton');
  const profileCameraStream = document.getElementById('profileCameraStream');
  const takeProfilePictureButton = document.getElementById('takeProfilePictureButton');
  const tabs = document.querySelectorAll('.tab');

  // App state
  let appState = {
    connected: false,
    cameraActive: false,
    stream: null,
    capturedImage: null,
    profileMetadata: [],
    currentProfileId: null
  };

  // Initialize the page
  initializePage();

  // Event listeners
  addProfileButton.addEventListener('click', showAddProfileModal);
  closeProfileModal.addEventListener('click', closeModal);
  closeAddProfileModal.addEventListener('click', closeModal);
  profilePhotoPreview.addEventListener('click', startProfileCamera);
  closeProfileCameraButton.addEventListener('click', stopProfileCamera);
  takeProfilePictureButton.addEventListener('click', takeProfilePicture);
  addMetadataButton.addEventListener('click', addMetadataItem);
  saveProfileButton.addEventListener('click', saveProfile);

  // Tab navigation
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const tabName = this.getAttribute('data-tab');
      navigateToTab(tabName);
    });
  });

  // Initialize the page
  function initializePage() {
    // Check server connection
    checkServerStatus()
      .then(status => {
        if (status.online) {
          setConnected(true);
          
          // Load profiles
          loadProfiles();
        } else {
          setConnected(false);
          showError('Could not connect to Robin AI server. Please try again later.');
        }
      })
      .catch(error => {
        console.error('Error initializing page:', error);
        setConnected(false);
      });
  }

  // Check server status
  function checkServerStatus() {
    return fetch('/api/status')
      .then(response => {
        if (!response.ok) {
          throw new Error('Server status check failed');
        }
        return response.json();
      });
  }

  // Load profiles
  function loadProfiles() {
    fetch('/api/profiles')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load profiles');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Render profiles
          renderProfiles(data.profiles);
        } else {
          throw new Error(data.error || 'Failed to load profiles');
        }
      })
      .catch(error => {
        console.error('Error loading profiles:', error);
        profilesContainer.innerHTML = '<div class="empty-message">No profiles available or error loading profiles.</div>';
      });
  }

  // Render profiles
  function renderProfiles(profiles) {
    profilesContainer.innerHTML = '';
    
    if (!profiles || profiles.length === 0) {
      profilesContainer.innerHTML = '<div class="empty-message">No face profiles have been created yet.</div>';
      return;
    }
    
    profiles.forEach(profile => {
      const profileCard = document.createElement('div');
      profileCard.className = 'profile-card';
      profileCard.dataset.id = profile.id;
      
      // Format last seen time
      const lastSeen = profile.last_seen ? new Date(profile.last_seen) : null;
      const lastSeenText = lastSeen ? formatTimeAgo(lastSeen) : 'Never';
      
      // Get metadata count
      const metadataCount = profile.metadata ? Object.keys(profile.metadata).length : 0;
      
      profileCard.innerHTML = `
        <div class="profile-header">
          <div class="profile-image">
            ${profile.image_path ? 
              `<img src="${profile.image_path}" alt="${profile.name}">` : 
              profile.name.charAt(0).toUpperCase()}
          </div>
          <div class="profile-info">
            <div class="profile-name">${profile.name}</div>
            <div class="profile-meta">
              <span><i class="fas fa-calendar"></i> Added: ${new Date(profile.created_at).toLocaleDateString()}</span>
              <span><i class="fas fa-tag"></i> Metadata: ${metadataCount}</span>
            </div>
          </div>
        </div>
        <div class="profile-footer">
          <div>Last seen: ${lastSeenText}</div>
          <div class="profile-actions">
            <button class="profile-action-btn view" title="View Profile"><i class="fas fa-eye"></i></button>
            <button class="profile-action-btn delete" title="Delete Profile"><i class="fas fa-trash"></i></button>
          </div>
        </div>
      `;
      
      // Add click event to view profile
      const viewButton = profileCard.querySelector('.profile-action-btn.view');
      viewButton.addEventListener('click', (e) => {
        e.stopPropagation();
        viewProfile(profile);
      });
      
      // Add click event to delete profile
      const deleteButton = profileCard.querySelector('.profile-action-btn.delete');
      deleteButton.addEventListener('click', (e) => {
        e.stopPropagation();
        confirmDeleteProfile(profile.id, profile.name);
      });
      
      // Add click event to the whole card
      profileCard.addEventListener('click', () => {
        viewProfile(profile);
      });
      
      profilesContainer.appendChild(profileCard);
    });
  }

  // Format time ago (e.g., "2 hours ago", "3 days ago")
  function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = Math.floor(seconds / 31536000);
    if (interval > 1) return interval + ' years ago';
    
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) return interval + ' months ago';
    
    interval = Math.floor(seconds / 86400);
    if (interval > 1) return interval + ' days ago';
    
    interval = Math.floor(seconds / 3600);
    if (interval > 1) return interval + ' hours ago';
    
    interval = Math.floor(seconds / 60);
    if (interval > 1) return interval + ' minutes ago';
    
    if (seconds < 10) return 'just now';
    
    return Math.floor(seconds) + ' seconds ago';
  }

  // View profile
  function viewProfile(profile) {
    profileModalTitle.textContent = profile.name;
    
    let imageSrc = '';
    if (profile.image_path) {
      imageSrc = `background-image: url('${profile.image_path}');`;
    }
    
    let metadataHTML = '';
    if (profile.metadata) {
      Object.entries(profile.metadata).forEach(([key, value]) => {
        metadataHTML += `
          <div class="detail-item">
            <div class="detail-label">${key}</div>
            <div class="detail-value">${value}</div>
          </div>
        `;
      });
    }
    
    if (!metadataHTML) {
      metadataHTML = '<div class="empty-metadata">No metadata available</div>';
    }
    
    const lastSeen = profile.last_seen ? new Date(profile.last_seen).toLocaleString() : 'Never';
    
    profileModalBody.innerHTML = `
      <div class="profile-details">
        <div class="profile-detail-image" style="${imageSrc}"></div>
        
        <div class="profile-detail-section">
          <h4>Basic Information</h4>
          <div class="detail-item">
            <div class="detail-label">ID</div>
            <div class="detail-value">${profile.id}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Created</div>
            <div class="detail-value">${new Date(profile.created_at).toLocaleString()}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Last Seen</div>
            <div class="detail-value">${lastSeen}</div>
          </div>
        </div>
        
        <div class="profile-detail-section">
          <h4>Metadata</h4>
          ${metadataHTML}
        </div>
      </div>
    `;
    
    profileModal.classList.add('visible');
  }

  // Confirm delete profile
  function confirmDeleteProfile(id, name) {
    if (confirm(`Are you sure you want to delete the profile for ${name}? This action cannot be undone.`)) {
      deleteProfile(id);
    }
  }

  // Delete profile
  function deleteProfile(id) {
    fetch(`/api/profiles/${id}`, {
      method: 'DELETE'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to delete profile');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Refresh profiles
        loadProfiles();
      } else {
        throw new Error(data.error || 'Failed to delete profile');
      }
    })
    .catch(error => {
      console.error('Error deleting profile:', error);
      alert('Failed to delete profile. Please try again.');
    });
  }

  // Show add profile modal
  function showAddProfileModal() {
    // Reset form
    profileName.value = '';
    profilePhotoPreview.style.backgroundImage = '';
    profilePhotoPreview.innerHTML = `
      <i class="fas fa-camera"></i>
      <span>Tap to take a photo</span>
    `;
    metadataList.innerHTML = '';
    appState.profileMetadata = [];
    appState.capturedImage = null;
    
    // Show modal
    addProfileModal.classList.add('visible');
  }

  // Close any open modal
  function closeModal() {
    profileModal.classList.remove('visible');
    addProfileModal.classList.remove('visible');
  }

  // Start profile camera
  function startProfileCamera() {
    if (appState.cameraActive) {
      return; // Already active
    }
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('Camera access is not supported by your browser.');
      return;
    }
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
      .then(stream => {
        appState.stream = stream;
        profileCameraStream.srcObject = stream;
        profileCameraView.classList.add('visible');
        appState.cameraActive = true;
      })
      .catch(error => {
        console.error('Error accessing camera:', error);
        alert('Could not access camera. Please check your camera permissions.');
      });
  }

  // Stop profile camera
  function stopProfileCamera() {
    if (appState.cameraActive && appState.stream) {
      // Stop all tracks in the stream
      appState.stream.getTracks().forEach(track => track.stop());
      profileCameraStream.srcObject = null;
      appState.stream = null;
    }
    
    profileCameraView.classList.remove('visible');
    appState.cameraActive = false;
  }

  // Take profile picture
  function takeProfilePicture() {
    if (!appState.cameraActive) {
      return;
    }
    
    try {
      // Create a canvas element to capture the image
      const canvas = document.createElement('canvas');
      canvas.width = profileCameraStream.videoWidth;
      canvas.height = profileCameraStream.videoHeight;
      const context = canvas.getContext('2d');
      
      // Draw the video frame to the canvas
      context.drawImage(profileCameraStream, 0, 0, canvas.width, canvas.height);
      
      // Get the data URL
      const dataUrl = canvas.toDataURL('image/jpeg');
      
      // Update the preview
      profilePhotoPreview.style.backgroundImage = `url('${dataUrl}')`;
      profilePhotoPreview.innerHTML = '';
      
      // Store the captured image
      canvas.toBlob(blob => {
        appState.capturedImage = blob;
      }, 'image/jpeg');
      
      // Stop the camera
      stopProfileCamera();
    } catch (error) {
      console.error('Error taking picture:', error);
      alert('Failed to capture image. Please try again.');
    }
  }

  // Add metadata item
  function addMetadataItem() {
    const key = metadataKey.value.trim();
    const value = metadataValue.value.trim();
    
    if (!key || !value) {
      alert('Both key and value are required for metadata.');
      return;
    }
    
    // Check for duplicate keys
    if (appState.profileMetadata.some(item => item.key === key)) {
      alert('A metadata item with this key already exists.');
      return;
    }
    
    // Add to state
    appState.profileMetadata.push({ key, value });
    
    // Add to UI
    const metadataItem = document.createElement('div');
    metadataItem.className = 'metadata-item';
    metadataItem.innerHTML = `
      <div class="metadata-item-content">${key}: ${value}</div>
      <button class="metadata-item-remove" data-key="${key}"><i class="fas fa-times"></i></button>
    `;
    
    // Add delete event
    metadataItem.querySelector('.metadata-item-remove').addEventListener('click', function() {
      const key = this.getAttribute('data-key');
      appState.profileMetadata = appState.profileMetadata.filter(item => item.key !== key);
      metadataItem.remove();
    });
    
    metadataList.appendChild(metadataItem);
    
    // Clear inputs
    metadataKey.value = '';
    metadataValue.value = '';
    metadataKey.focus();
  }

  // Save profile
  function saveProfile() {
    const name = profileName.value.trim();
    
    if (!name) {
      alert('Profile name is required.');
      return;
    }
    
    if (!appState.capturedImage) {
      alert('Please take a profile picture.');
      return;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', appState.capturedImage, 'profile.jpg');
    
    // Add metadata
    if (appState.profileMetadata.length > 0) {
      formData.append('metadata', JSON.stringify(
        appState.profileMetadata.reduce((obj, item) => {
          obj[item.key] = item.value;
          return obj;
        }, {})
      ));
    }
    
    // Send to API
    fetch('/api/profiles', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to save profile');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Close modal
        closeModal();
        
        // Refresh profiles
        loadProfiles();
      } else {
        throw new Error(data.error || 'Failed to save profile');
      }
    })
    .catch(error => {
      console.error('Error saving profile:', error);
      alert('Failed to save profile. Please try again.');
    });
  }

  // Set connection status
  function setConnected(connected) {
    appState.connected = connected;
    
    if (connected) {
      userStatus.classList.add('online');
      userStatus.querySelector('.status-text').textContent = 'Online';
    } else {
      userStatus.classList.remove('online');
      userStatus.querySelector('.status-text').textContent = 'Offline';
    }
  }

  // Show error message
  function showError(message) {
    // Add error toast or notification if needed
    console.error(message);
  }

  // Navigate to tab
  function navigateToTab(tabName) {
    switch (tabName) {
      case 'home':
        window.location.href = '/mobile';
        break;
      case 'emotions':
        window.location.href = '/mobile/emotions';
        break;
      case 'profiles':
        // Already on profiles page
        break;
      case 'settings':
        window.location.href = '/mobile/settings';
        break;
    }
  }
});