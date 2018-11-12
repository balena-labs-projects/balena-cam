# balena-cam

Share your balena device's camera feed.

## Getting started

- Sign up on [balena.io](https://balena.io/) and follow our [Getting Started Guide](https://balena.io/docs/learn/getting-started)
- Clone this repository to your local workspace
- Set these variables in the `Fleet Configuration` application side tab
  - `RESIN_HOST_CONFIG_gpu_mem` = `196`
  - `RESIN_HOST_CONFIG_start_x` = `1`
- Push code to your device with a simple `git push balena master`
- See the magic happening, your device is getting updated Over-The-Air!
- If you want your device to be accessible on WAN, enable its public URL
  - Select your device from the `Devices` side tab
  - Click the `Actions` side tab
  - Click the `ENABLE PUBLIC DEVICE URL` button
  - Note down your device's public URL!
- When your device finishes updating visit your device's public URL to watch your stream!
- You can find your device's IP on the Balena dashboard.
- Make sure to update your devices after every change you make!
- Commit your changes and do another `git push balena master`

## Additional Information

- This project uses [WebRTC](https://webrtc.org/) (a Real-Time Communication protocol).
- A direct WebRTC connection fails in some cases.
- This current version works on all the cases that a direct connection is possible.

## License

Copyright 2018 Balena Ltd.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
