var primaryPeerConnection = null;
var backupPeerConnection = null;
var vfdIntervalId = null;
var state = 0;

window.onbeforeunload = function() {
  if (primaryPeerConnection !== null) {
    primaryPeerConnection.close();
  }
};

function attachStreamToVideoElement(pc, videoElem){
  console.log('Attaching stream...');
  videoElem.srcObject = pc.getRemoteStreams()[0];
}

function peerConnectionGood(pc) {
  return ((pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed'));
}

function peerConnectionBad(pc) {
  return ((pc.iceConnectionState === 'disconnected' || pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'closed'));
}

function hideAllContainers() {
    document.getElementById('spinner-container').style.display = 'none';
    document.getElementById('video-container').style.display = 'none';
    document.getElementById('fail-container').style.display = 'none';
    document.getElementById('mjpeg-container').style.display = 'none';
}

function showContainer(kind) {
  hideAllContainers();
  if (kind === 'video') {
    document.getElementById('video-container').style.display = 'block';
  } else if (kind === 'fail') {
    document.getElementById('fail-container').style.display = 'initial';
  } else if (kind === 'mjpeg') {
    document.getElementById('mjpeg-container').style.display = 'block';
  } else {
    console.error('No container that is kind of: ' + kind);
  }
}

function createNewPeerConnection() {
  var pc = new RTCPeerConnection({sdpSemantics: 'unified-plan'});
  var isVideoAttached = false;
  new Promise(function (resolve, reject) {
    function mainIceListener() {
      console.warn(pc.iceConnectionState);
      if  (peerConnectionBad(pc)){
        if (state == 0) {
          //this means webrtc connection is not possible
          state = 2;
          startMJPEG();
        }
        if (state !== 2) {
          showContainer('fail');
        }
      }
      if (peerConnectionGood(pc)) {
        document.getElementById('webrtc').style.display = 'initial';
        if (!isVideoAttached) {
          if (state === 0) {
            state = 1;
          }
          isVideoAttached = true;
          attachStreamToVideoElement(pc, document.getElementById('video'));
          cleanup();
          startVideoFreezeDetection(pc);
        }
        showContainer('video');
      }
    }
    pc.addEventListener('iceconnectionstatechange', mainIceListener);
    resolve();
  }).then(function () {
    pc.addTransceiver('video', {direction: 'recvonly'});
    return pc.createOffer()
  }).then(function(offer) {
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
  return pc
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
    setTimeout(requestFullscreen(video), 100);
  }
}

// Use on firefox
function getCurrentFrame() {
    var canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    var canvasContext = canvas.getContext("2d");
    canvasContext.drawImage(video, 0, 0);
    return canvas.toDataURL('image/png');
}

function isVideoFrozen(pc) {
  var previousFrame;
  var ignoreFirst = true;
  vfdIntervalId = setInterval(function() {
    if (peerConnectionGood(pc) && video.currentTime > 0 && getCurrentFrame() === previousFrame) {
      if (ignoreFirst) {
        ignoreFirst = false;
        return
      }
      console.warn("Video freeze detected using frames!!!");
      reconnect();
    } else {
      previousFrame = getCurrentFrame();
    }
  }, 3000);
}

// Use on Chrome
function checkVideoFreeze(pc) {
  var previousPlaybackTime;
  vfdIntervalId = setInterval(function() {
    if (peerConnectionGood(pc) && previousPlaybackTime === video.currentTime && video.currentTime !== 0) {
      console.warn("Video freeze detected!!!");
      reconnect();
    } else {
      previousPlaybackTime = video.currentTime;
    }
  }, 3000);
}

function startVideoFreezeDetection(pc) {
  stopVideoFreezeDetection();
  if (navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
    isVideoFrozen(pc);
  } else {
    checkVideoFreeze(pc);
  }
}

function stopVideoFreezeDetection() {
  if (vfdIntervalId !== null) {
    console.log('Stopping Current Video Freeze Detector');
    clearInterval(vfdIntervalId);
  }
}

function cleanup() {
  if (backupPeerConnection !== null) {
    console.log('Cleaning Up...')
    var tmp = primaryPeerConnection;
    primaryPeerConnection = backupPeerConnection;
    backupPeerConnection = tmp;
    backupPeerConnection.close();
    backupPeerConnection = null;
    var thisInterval = setInterval(function (){
      if (peerConnectionGood(primaryPeerConnection) && backupPeerConnection === null) {
        showContainer('video');
        clearInterval(thisInterval);
      }
    }, 100);
  }
}

function reconnect() {
  console.log('Reconnecting');
  backupPeerConnection = createNewPeerConnection();
}

function startMJPEG() {
  document.getElementById('vpn').style.display = 'initial';
  console.warn('WebRTC does not work! Starting MJPEG streaming.')
  primaryPeerConnection.close();
  primaryPeerConnection = null;
  var mjpeg = new Image();
  mjpeg.className = 'img-fluid';
  mjpeg.src = '/mjpeg';
  document.getElementById('mjpeg').appendChild(mjpeg);
  showContainer('mjpeg')
}

primaryPeerConnection = createNewPeerConnection();
