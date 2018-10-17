var pc = new RTCPeerConnection({sdpSemantics: 'unified-plan'});

// register some listeners to help debugging
pc.addEventListener('icegatheringstatechange', function() {
  console.warn(pc.iceGatheringState);
}, false);

pc.addEventListener('iceconnectionstatechange', function() {
  console.warn(pc.iceConnectionState);
  if ((typeof pc.iceConnectionState !== 'undefined') && (pc.iceConnectionState === 'disconnected' || pc.iceConnectionState === 'failed')) {
        document.getElementById('video-container').style.display = 'none';
        document.getElementById('fail-container').style.display = 'initial';
  }
}, false);

pc.addEventListener('signalingstatechange', function() {
     console.warn(pc.signalingState);
}, false);

// connect audio / video
pc.addEventListener('track', function(evt) {
    console.log('incoming track')
    console.log(evt);
    if (evt.track.kind == 'video') {
        document.getElementById('spinner-container').style.display = 'none';
        document.getElementById('video').srcObject = evt.streams[0];
        console.log('video elem added');
    } else {
        document.getElementById('audio').srcObject = evt.streams[0];
    }
});

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

function stop() {
    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
}
negotiate()
