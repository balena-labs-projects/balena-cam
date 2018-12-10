package main

import (
	"fmt"
	"net/http"
	"encoding/json"
	"io/ioutil"
	"github.com/pions/webrtc"
	"github.com/pions/webrtc/examples/util"
	"github.com/pions/webrtc/examples/util/gstreamer-src"
	"github.com/pions/webrtc/pkg/ice"
)

func handleOffer(w http.ResponseWriter, r *http.Request){
	// extract offerer's sdp from json data
	var offer webrtc.RTCSessionDescription
	body, err := ioutil.ReadAll(r.Body)
	util.Check(err)
	err = json.Unmarshal(body, &offer)
	util.Check(err)
	// WebRTC
	webrtc.RegisterDefaultCodecs()
	config := webrtc.RTCConfiguration {
		IceServers: []webrtc.RTCIceServer {
			{
				URLs: []string{"stun:stun.l.google.com:19302"},
			},
		},
	}
	peerConnection, err := webrtc.New(config)
	util.Check(err)
	peerConnection.OnICEConnectionStateChange(func(connectionState ice.ConnectionState) {
		fmt.Printf("Connection State has changed %s \n", connectionState.String())
	})
	// Create Video Track
	vp8Track, err := peerConnection.NewRTCSampleTrack(webrtc.DefaultPayloadTypeVP8, "video", "pion2")
	util.Check(err)
	_, err = peerConnection.AddTrack(vp8Track)
	util.Check(err)
	// Set offer
	err = peerConnection.SetRemoteDescription(offer)
	util.Check(err)
	answer, err := peerConnection.CreateAnswer(nil)
	util.Check(err)
	// Make and Send answer back to the client
	answerJson, err := json.Marshal(answer)
	util.Check(err)
	gst.CreatePipeline(webrtc.VP8, vp8Track.Samples).Start()

	// Response
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(answerJson)
}

func main(){
	// Web Server
	dir := http.FileServer(http.Dir("client"))
	http.Handle("/", dir)
	http.HandleFunc("/offer", handleOffer)
	fmt.Println("Server running...")
	fmt.Println("http://localhost:3000")
	http.ListenAndServe(":3000", nil)
}

