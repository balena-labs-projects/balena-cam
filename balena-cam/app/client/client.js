var pc = new RTCPeerConnection({sdpSemantics: 'unified-plan'});

pc.addEventListener('icegatheringstatechange', function() {
  console.warn(pc.iceGatheringState);
}, false);

pc.addEventListener('iceconnectionstatechange', function() {
  console.warn(pc.iceConnectionState);
  if  (peerConnectionBad()){
    showContainer('fail');
  }
  if (peerConnectionGood()) {
    showContainer('video');
  }
}, false);

pc.addEventListener('signalingstatechange', function() {
  console.warn(pc.signalingState);
}, false);

pc.addEventListener('track', function(evt) {
  console.log('incoming track')
  if (evt.track.kind == 'video') {
    document.getElementById('video').srcObject = evt.streams[0];
    console.log('Video element added.');
  }
});

function peerConnectionGood() {
  return ((typeof pc.iceConnectionState !== 'undefined') && (pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed'));
}

function peerConnectionBad() {
  return ((typeof pc.iceConnectionState !== 'undefined') && (pc.iceConnectionState === 'disconnected' || pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'closed'));
}

function showContainer(kind){
  if (kind === 'video') {
    document.getElementById('spinner-container').style.display = 'none';
    document.getElementById('video-container').style.display = 'block';
    document.getElementById('fail-container').style.display = 'none';
  } else if (kind === 'fail') {
    document.getElementById('spinner-container').style.display = 'none';
    document.getElementById('video-container').style.display = 'none';
    document.getElementById('fail-container').style.display = 'initial';
  } else {
    console.error('No container that is kind of: ' + kind);
  }
}

function negotiate() {
  pc.addTransceiver('video', {direction: 'recvonly'});
  return pc.createOffer().then(function(offer) {
    return pc.setLocalDescription(offer);
  }).then(function() {
    // wait for ICE gathering to complete
    return new Promise(function(resolve) {
      if (pc.iceGatheringState === 'complete') {
        resolve();
      } else {
        function checkState() {
          if (pc.iceGatheringState === 'complete') {
            pc.removeEventListener('icegatheringstatechange', checkState);
            resolve();
          }
        }
        pc.addEventListener('icegatheringstatechange', checkState);
      }
    });
  }).then(function() {
    var offer = pc.localDescription;
    console.log('Offer SDP');
    console.log(offer.sdp);
    return fetch('/offer', {
      body: JSON.stringify({
        sdp: offer.sdp,
        type: offer.type,
      }),
      headers: {
        'Content-Type': 'application/json'
      },
      method: 'POST'
    });
  }).then(function(response) {
    return response.json();
  }).then(function(answer) {
    console.log('Answer SDP');
    console.log(answer.sdp);
    return pc.setRemoteDescription(answer);
  }).catch(function(e){
    console.error(e);
  });
}

function supportsFullscreen() {
  return (document.body.mozRequestFullScreen || document.body.webkitRequestFullScreen || document.body.requestFullScreen);
}

function requestFullscreen(element) {
  return ((element.mozRequestFullScreen && element.mozRequestFullScreen()) ||
  (element.webkitRequestFullScreen && element.webkitRequestFullScreen()) ||
  (element.requestFullScreen && element.requestFullScreen()));
}

function fullscreen() {
  var video = document.getElementById('video');
  if (supportsFullscreen()) {
    requestFullscreen(video);
  }
}

function checkVideoFreeze() {
  setInterval(function() {
    if (peerConnectionGood() && previousPlaybackTime === video.currentTime && video.currentTime !== 0) {
      console.warn("Video freeze detected!!!");
      pc.close();
      location.reload();
    } else {
      previousPlaybackTime = video.currentTime;
    }
  }, 3000);
}

negotiate();
checkVideoFreeze();
