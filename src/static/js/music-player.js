/**
 * Music Player using HTML5 Audio API
 * Provides play/pause/skip controls, progress bar, volume control, and queue management
 */

class MusicPlayer {
  constructor() {
    this.audio = new Audio();
    this.currentTrackIndex = 0;
    this.queue = [];
    this.isPlaying = false;
    this.isShuffled = false;
    this.repeatMode = 'none'; // none, one, all
    
    this.initializeElements();
    this.attachEventListeners();
    this.loadState();
    this.updateUI();
  }

  initializeElements() {
    // Player controls
    this.playPauseBtn = document.getElementById('play-pause-btn');
    this.prevBtn = document.getElementById('prev-btn');
    this.nextBtn = document.getElementById('next-btn');
    this.shuffleBtn = document.getElementById('shuffle-btn');
    this.repeatBtn = document.getElementById('repeat-btn');
    
    // Progress
    this.progressBar = document.getElementById('progress-bar');
    this.progressFill = document.getElementById('progress-fill');
    this.currentTimeEl = document.getElementById('current-time');
    this.totalTimeEl = document.getElementById('total-time');
    
    // Volume
    this.volumeSlider = document.getElementById('volume-slider');
    this.volumeIcon = document.getElementById('volume-icon');
    
    // Now playing
    this.trackTitle = document.getElementById('track-title');
    this.trackArtist = document.getElementById('track-artist');
    this.albumArt = document.getElementById('album-art');
    
    // Queue
    this.queueList = document.getElementById('queue-list');
    this.queueToggle = document.getElementById('queue-toggle');
    this.queuePanel = document.getElementById('queue-panel');
    
    // Player container
    this.playerContainer = document.getElementById('music-player');
  }

  attachEventListeners() {
    // Audio events
    this.audio.addEventListener('timeupdate', () => this.onTimeUpdate());
    this.audio.addEventListener('ended', () => this.onTrackEnded());
    this.audio.addEventListener('loadedmetadata', () => this.onMetadataLoaded());
    this.audio.addEventListener('play', () => this.onPlay());
    this.audio.addEventListener('pause', () => this.onPause());
    this.audio.addEventListener('error', (e) => this.onError(e));
    
    // Control events
    this.playPauseBtn?.addEventListener('click', () => this.togglePlayPause());
    this.prevBtn?.addEventListener('click', () => this.playPrevious());
    this.nextBtn?.addEventListener('click', () => this.playNext());
    this.shuffleBtn?.addEventListener('click', () => this.toggleShuffle());
    this.repeatBtn?.addEventListener('click', () => this.toggleRepeat());
    
    // Progress bar
    this.progressBar?.addEventListener('click', (e) => this.seek(e));
    
    // Volume
    this.volumeSlider?.addEventListener('input', (e) => this.setVolume(e.target.value));
    this.volumeIcon?.addEventListener('click', () => this.toggleMute());
    
    // Queue
    this.queueToggle?.addEventListener('click', () => this.toggleQueue());
  }

  togglePlayPause() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    if (this.queue.length === 0) {
      console.log('No tracks in queue');
      return;
    }
    
    if (!this.audio.src || this.audio.src === '') {
      this.loadTrack(this.currentTrackIndex);
    }
    
    this.audio.play().catch(error => {
      console.error('Error playing audio:', error);
    });
  }

  pause() {
    this.audio.pause();
  }

  playNext() {
    if (this.queue.length === 0) return;
    
    this.currentTrackIndex++;
    if (this.currentTrackIndex >= this.queue.length) {
      this.currentTrackIndex = 0;
    }
    
    this.loadTrack(this.currentTrackIndex);
    this.play();
  }

  playPrevious() {
    if (this.queue.length === 0) return;
    
    // If more than 3 seconds in, restart current track
    if (this.audio.currentTime > 3) {
      this.audio.currentTime = 0;
      return;
    }
    
    this.currentTrackIndex--;
    if (this.currentTrackIndex < 0) {
      this.currentTrackIndex = this.queue.length - 1;
    }
    
    this.loadTrack(this.currentTrackIndex);
    this.play();
  }

  loadTrack(index) {
    if (index < 0 || index >= this.queue.length) return;
    
    const track = this.queue[index];
    this.currentTrackIndex = index;
    
    this.audio.src = track.url;
    this.trackTitle.textContent = track.title || 'Unknown Track';
    this.trackArtist.textContent = track.artist || 'Unknown Artist';
    
    if (track.albumArt) {
      this.albumArt.src = track.albumArt;
      this.albumArt.style.display = 'block';
    } else {
      this.albumArt.style.display = 'none';
    }
    
    this.updateQueueUI();
    this.saveState();
  }

  seek(event) {
    if (!this.audio.duration || isNaN(this.audio.duration)) return;
    
    const rect = this.progressBar.getBoundingClientRect();
    const percent = (event.clientX - rect.left) / rect.width;
    this.audio.currentTime = percent * this.audio.duration;
  }

  setVolume(value) {
    this.audio.volume = value / 100;
    this.updateVolumeIcon();
    this.saveState();
  }

  toggleMute() {
    if (this.audio.volume > 0) {
      this.audio.volume = 0;
      this.volumeSlider.value = 0;
    } else {
      this.audio.volume = 0.7;
      this.volumeSlider.value = 70;
    }
    this.updateVolumeIcon();
    this.saveState();
  }

  toggleShuffle() {
    this.isShuffled = !this.isShuffled;
    this.shuffleBtn.classList.toggle('active', this.isShuffled);
    this.saveState();
  }

  toggleRepeat() {
    const modes = ['none', 'all', 'one'];
    const currentIndex = modes.indexOf(this.repeatMode);
    this.repeatMode = modes[(currentIndex + 1) % modes.length];
    
    this.repeatBtn.classList.remove('repeat-none', 'repeat-all', 'repeat-one');
    this.repeatBtn.classList.add(`repeat-${this.repeatMode}`);
    this.repeatBtn.classList.toggle('active', this.repeatMode !== 'none');
    
    this.saveState();
  }

  toggleQueue() {
    this.queuePanel.classList.toggle('open');
  }

  addToQueue(track) {
    this.queue.push(track);
    this.updateQueueUI();
    this.saveState();
    
    // If this is the first track, load it
    if (this.queue.length === 1) {
      this.loadTrack(0);
    }
  }

  removeFromQueue(index) {
    if (index < 0 || index >= this.queue.length) return;
    
    this.queue.splice(index, 1);
    
    // Adjust current index if needed
    if (this.currentTrackIndex >= index && this.currentTrackIndex > 0) {
      this.currentTrackIndex--;
    }
    
    if (this.queue.length === 0) {
      this.pause();
      this.audio.src = '';
      this.trackTitle.textContent = 'No track playing';
      this.trackArtist.textContent = '';
      this.albumArt.style.display = 'none';
    } else if (index === this.currentTrackIndex) {
      this.loadTrack(this.currentTrackIndex);
    }
    
    this.updateQueueUI();
    this.saveState();
  }

  playTrackFromQueue(index) {
    if (index < 0 || index >= this.queue.length) return;
    
    this.loadTrack(index);
    this.play();
  }

  clearQueue() {
    this.queue = [];
    this.currentTrackIndex = 0;
    this.pause();
    this.audio.src = '';
    this.trackTitle.textContent = 'No track playing';
    this.trackArtist.textContent = '';
    this.albumArt.style.display = 'none';
    this.updateQueueUI();
    this.saveState();
  }

  updateQueueUI() {
    if (!this.queueList) return;
    
    this.queueList.innerHTML = '';
    
    if (this.queue.length === 0) {
      this.queueList.innerHTML = '<div class="queue-empty">Queue is empty</div>';
      return;
    }
    
    this.queue.forEach((track, index) => {
      const item = document.createElement('div');
      item.className = 'queue-item';
      if (index === this.currentTrackIndex) {
        item.classList.add('active');
      }
      
      item.innerHTML = `
        <div class="queue-item-info" data-index="${index}">
          <div class="queue-item-title">${track.title || 'Unknown Track'}</div>
          <div class="queue-item-artist">${track.artist || 'Unknown Artist'}</div>
        </div>
        <button class="queue-item-remove" data-index="${index}" aria-label="Remove from queue">×</button>
      `;
      
      // Play on click
      item.querySelector('.queue-item-info').addEventListener('click', () => {
        this.playTrackFromQueue(index);
      });
      
      // Remove on click
      item.querySelector('.queue-item-remove').addEventListener('click', (e) => {
        e.stopPropagation();
        this.removeFromQueue(index);
      });
      
      this.queueList.appendChild(item);
    });
  }

  onTimeUpdate() {
    if (!this.audio.duration) return;
    
    const percent = (this.audio.currentTime / this.audio.duration) * 100;
    this.progressFill.style.width = `${percent}%`;
    
    this.currentTimeEl.textContent = this.formatTime(this.audio.currentTime);
  }

  onMetadataLoaded() {
    this.totalTimeEl.textContent = this.formatTime(this.audio.duration);
  }

  onPlay() {
    this.isPlaying = true;
    this.playPauseBtn.innerHTML = '⏸';
    this.playPauseBtn.setAttribute('aria-label', 'Pause');
    this.saveState();
  }

  onPause() {
    this.isPlaying = false;
    this.playPauseBtn.innerHTML = '▶';
    this.playPauseBtn.setAttribute('aria-label', 'Play');
    this.saveState();
  }

  onTrackEnded() {
    if (this.repeatMode === 'one') {
      this.audio.currentTime = 0;
      this.play();
    } else if (this.repeatMode === 'all' || this.currentTrackIndex < this.queue.length - 1) {
      this.playNext();
    } else {
      this.pause();
    }
  }

  onError(error) {
    console.error('Audio error:', error);
    
    // Show user-friendly error message
    const currentTrack = this.queue[this.currentTrackIndex];
    if (currentTrack) {
      this.trackTitle.textContent = `Error loading: ${currentTrack.title || 'Unknown Track'}`;
    }
    
    // Try to skip to next track on error
    if (this.queue.length > 1) {
      setTimeout(() => this.playNext(), 2000);
    }
  }

  updateVolumeIcon() {
    const volume = this.audio.volume;
    if (volume === 0) {
      this.volumeIcon.textContent = '🔇';
    } else if (volume < 0.5) {
      this.volumeIcon.textContent = '🔉';
    } else {
      this.volumeIcon.textContent = '🔊';
    }
  }

  updateUI() {
    this.updateVolumeIcon();
    this.updateQueueUI();
    
    if (this.isPlaying) {
      this.playPauseBtn.innerHTML = '⏸';
    } else {
      this.playPauseBtn.innerHTML = '▶';
    }
    
    this.shuffleBtn.classList.toggle('active', this.isShuffled);
    this.repeatBtn.classList.remove('repeat-none', 'repeat-all', 'repeat-one');
    this.repeatBtn.classList.add(`repeat-${this.repeatMode}`);
    this.repeatBtn.classList.toggle('active', this.repeatMode !== 'none');
  }

  formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  saveState() {
    const state = {
      queue: this.queue,
      currentTrackIndex: this.currentTrackIndex,
      volume: this.audio.volume,
      isShuffled: this.isShuffled,
      repeatMode: this.repeatMode,
      currentTime: this.audio.currentTime
    };
    
    try {
      sessionStorage.setItem('musicPlayerState', JSON.stringify(state));
    } catch (e) {
      console.error('Error saving player state:', e);
    }
  }

  loadState() {
    try {
      const savedState = sessionStorage.getItem('musicPlayerState');
      if (!savedState) return;
      
      const state = JSON.parse(savedState);
      
      this.queue = state.queue || [];
      this.currentTrackIndex = state.currentTrackIndex || 0;
      this.isShuffled = state.isShuffled || false;
      this.repeatMode = state.repeatMode || 'none';
      
      if (state.volume !== undefined) {
        this.audio.volume = state.volume;
        this.volumeSlider.value = state.volume * 100;
      }
      
      if (this.queue.length > 0 && this.currentTrackIndex < this.queue.length) {
        this.loadTrack(this.currentTrackIndex);
        if (state.currentTime) {
          this.audio.currentTime = state.currentTime;
        }
      }
      
      this.updateUI();
    } catch (e) {
      console.error('Error loading player state:', e);
    }
  }
}

// Initialize player when DOM is ready
let musicPlayer;
document.addEventListener('DOMContentLoaded', function() {
  musicPlayer = new MusicPlayer();
  
  // Expose to global scope for easy access
  window.musicPlayer = musicPlayer;
  
  // Update queue count in the toggle button
  function updateQueueCount() {
    const queueToggle = document.getElementById('queue-toggle');
    if (queueToggle && musicPlayer) {
      queueToggle.textContent = `Queue (${musicPlayer.queue.length})`;
    }
  }
  
  // Override addToQueue to update count
  const originalAddToQueue = musicPlayer.addToQueue.bind(musicPlayer);
  musicPlayer.addToQueue = function(track) {
    originalAddToQueue(track);
    updateQueueCount();
  };
  
  // Override removeFromQueue to update count
  const originalRemoveFromQueue = musicPlayer.removeFromQueue.bind(musicPlayer);
  musicPlayer.removeFromQueue = function(index) {
    originalRemoveFromQueue(index);
    updateQueueCount();
  };
  
  // Override clearQueue to update count
  const originalClearQueue = musicPlayer.clearQueue.bind(musicPlayer);
  musicPlayer.clearQueue = function() {
    originalClearQueue();
    updateQueueCount();
  };
  
  // Add demo tracks (these are public domain audio samples for demonstration)
  // NOTE: External URLs are used for demo purposes. In production, consider:
  // - Hosting audio files locally
  // - Implementing proper error handling for unavailable resources
  // - Using a CDN for better performance
  function addDemoTracks() {
    const demoTracks = [
      {
        title: "Demo Track 1",
        artist: "Sample Artist",
        url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        albumArt: "https://via.placeholder.com/300x300/1db954/ffffff?text=Track+1"
      },
      {
        title: "Demo Track 2",
        artist: "Sample Artist",
        url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        albumArt: "https://via.placeholder.com/300x300/159c41/ffffff?text=Track+2"
      },
      {
        title: "Demo Track 3",
        artist: "Sample Artist",
        url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        albumArt: "https://via.placeholder.com/300x300/1db954/ffffff?text=Track+3"
      }
    ];
    
    // Only add demo tracks if queue is empty and no saved state exists
    const hasSavedState = sessionStorage.getItem('musicPlayerState');
    if (musicPlayer.queue.length === 0 && !hasSavedState) {
      demoTracks.forEach(track => musicPlayer.addToQueue(track));
    }
  }
  
  // Initialize with demo tracks
  updateQueueCount();
  
  // Expose addDemoTracks function for manual testing
  window.addDemoTracks = addDemoTracks;
});
