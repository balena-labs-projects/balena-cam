# Customization

Here are all the ways to currently customize your balenaCam setup. Additional features, fixes, and patches are welcome. See our contribution guide for more information.

## Password Protect your balenaCam device

To protect your balenaCam devices using a username and a password set the following environment variables.

| Key            | Value
|----------------|---------------------------
|**`username`**  | **`yourUserNameGoesHere`**
|**`password`**  | **`yourPasswordGoesHere`**

💡 **Tips:** 💡 
* You can set them as [fleet environment variables](https://www.balena.io/docs/learn/manage/serv-vars/#fleet-environment-and-service-variables) and every new balenaCam device you add will be password protected.
* You can set them as [device environment variables](https://www.balena.io/docs/learn/manage/serv-vars/#device-environment-and-service-variables) and the username and password will be different on each device.

## Optional Settings

- To rotate the camera feed by 180 degrees, add a **device variable**: `rotation` = `1` (More information about this on the [docs](https://www.balena.io/docs/learn/manage/serv-vars/)).
- To suppress any warnings, add a **device variable**: `PYTHONWARNINGS` = `ignore`

## TURN server configuration


If you have access to a TURN server and you want your balenaCam devices to use it. You can easily configure it using the following environment variables. When you set them all the app will use that TURN server as a fallback mechanism when a direct WebRTC connection is not possible.

| Key            | Value
|----------------|---------------------------
|**`STUN_SERVER`**  | **`stun:stun.l.google.com:19302`**
|**`TURN_SERVER`**  | **`turn:<yourTURNserverIP>:<yourTURNserverPORT>`**
|**`TURN_USERNAME`**  | **`<yourTURNserverUsername>`**
|**`TURN_PASSWORD`**  | **`yourTURNserverPassword`**