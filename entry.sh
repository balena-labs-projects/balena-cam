#!/bin/bash


echo "Video-streaming block started, waiting for other services to settle..."

# Allow time for capture/processing to start
sleep 8

# Set the port
if [[ -z $WEBRTC_PORT ]]
then
    port="80"
else
    port="$WEBRTC_PORT"
fi

# Get a list of running services using the Supervisor API
ser=$(curl -s "$BALENA_SUPERVISOR_ADDRESS/v2/applications/state?apikey=$BALENA_SUPERVISOR_API_KEY" | jq -r '.[].services | keys')

# If WEBRTC_RTSP_INPUT set, use that
if [[ -z $WEBRTC_RTSP_INPUT ]]
then
    if echo "$ser" | grep -q "video-processing"
    then
        echo "Found video-processing block, using that as video-streaming block input..."
        ./webrtc-streamer rtsp://localhost:8558/proc -H 0.0.0.0:"$port"
    elif echo "$ser" | grep -q "video-capture"
    then
        echo "Found video-capture block, using that as video-streaming block input..."
        ./webrtc-streamer rtsp://localhost:8554/server -H 0.0.0.0:"$port"
    else
        echo "No suitable video input found. Either add the processing or capture block, or set WEBRTC_RTSP_INPUT."
        echo "Sleeping for 30 seconds and then restarting..."
        sleep 30
    fi
else
    if [[ -z $WEBRTC_OPTIONS ]]
    then
        echo "Found WEBRTC_RTSP_INPUT, using $WEBRTC_RTSP_INPUT as video-capture block input..."
        ./webrtc-streamer "$WEBRTC_RTSP_INPUT" -H 0.0.0.0:"$port"
    else
        echo "Found WEBRTC_RTSP_INPUT and WEBRTC_OPTIONS. Setting video capture input to:"
        echo "$WEBRTC_RTSP_INPUT $WEBRTC_OPTIONS"
        ./webrtc-streamer "$WEBRTC_RTSP_INPUT" "$WEBRTC_OPTIONS"
    fi
        
fi
