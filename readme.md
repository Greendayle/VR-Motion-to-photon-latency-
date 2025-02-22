# Measuring Motion to Photon latency in wired and wireless headsets

Full results in collaboration are available on the bottom of this document

# Intro

The latency reported in most modern wireless headsets when using them as
PCVR headsets is often reported using built in debug tools in
Virtual Desktop, Pico Connect, SteamLink, Oculus Airlink, which show suspiciously low latencies.

Especially if we compare them with results from a `https://link.springer.com/content/pdf/10.3758/s13428-022-01983-5.pdf` article:

![results springer](./delays_springer.png)

Which made me suspicious and want to try to repeat that experiment.

# Methodology

I've tried to repeat the Springer article, but with some "ghetoisation"

I've made a vrchat world, which has a "test zone" area, which changes color,
depending if the right hand of the player is moving.

Movement is calculated using position of the right hand in this and previous frame,
if the distance between those positions is higher than a treshold - movement is detected and the testing zone changes color from green to red.

Treshold is calculated by placing the controller on a stable surface, and letting it rest for 4 seconds (click the Calibrate button). 
Maximum distance traveled between 2 consecutive frames in that time period + 10% is set as a threshold.

Two variants were used - plain colored and with voronoi noise overlaid - to increase scene complexity for video encoder.

The world is available here:

`https://vrchat.com/home/launch?worldId=wrld_8104befd-5540-424f-ba04-f1b39957d05c`

The tester code is as follows:

```csharp

using UdonSharp;
using UnityEngine;
using VRC.SDKBase;
using VRC.Udon;
using System;
using VRC.Udon.Common.Interfaces;
using TMPro;

public class MtPCalc : UdonSharpBehaviour
{
    double threshold = 0;
    double time_prev;
    double time_now;
    double fps;
    Vector3 current_pos;
    Vector3 previous_pos;
    double distance;
    VRCPlayerApi localPlayer;
    public bool calibrating = false;
    public Material movement;
    public Material no_movement;
    public Renderer test_zone;
    public TextMeshPro tresholdText;
    public TextMeshPro timerText;
    public TextMeshPro distanceText;
    public TextMeshPro fpsText;


    void Start()
    {

        localPlayer = Networking.LocalPlayer;
    }

    public void Calibrate()
    {
        calibrating = true;
        threshold = 0;
        SendCustomEventDelayedSeconds("CalibrateEnd", 4f);
    }

    public void CalibrateEnd()
    {
        calibrating = false;
        threshold = threshold * 1.1f;
    }

    void Update()
    {
        time_now = Time.time;
        fps = 1 / (time_now - time_prev);
        time_prev = time_now;
        fpsText.text = fps.ToString("F0");
        tresholdText.text = threshold.ToString("F2");
        timerText.text = Time.time.ToString("F3");
        //if (localPlayer != null && localPlayer.IsUserInVR())
        if (localPlayer != null)

            {
                previous_pos = current_pos;
            current_pos = localPlayer.GetTrackingData(VRCPlayerApi.TrackingDataType.RightHand).position;
            distance = Math.Sqrt((previous_pos.x - current_pos.x) * (previous_pos.x - current_pos.x) + (previous_pos.y - current_pos.y) * (previous_pos.y - current_pos.y) + (previous_pos.z - current_pos.z) * (previous_pos.z - current_pos.z)) * 1000.0;

            if (calibrating)
            {
                threshold = Math.Max(distance, threshold);
            }
            Material[] mats = test_zone.materials;

            if (distance > threshold)
            {
                mats[0] = movement;

            }
            else
            {
                mats[0] = no_movement;
            }

            test_zone.materials = mats;
            distanceText.text = distance.ToString("F2");
        }
    }

}
```

## Software/Hardware used

+ Camera: Oppo Reno 7 smartphone with 120 FPS slow mo camera mode.
+ SteamVR 2.9.2
+ Vrchat Build 1550
+ Pico Connect: 10.2.7
+ Vive Pro 2 with Knuckles Controllers
+ Vive with Knuckles Controllers
+ Pico 4
+ Technicolor TC 7200 wifi router (yea, it's bad)
+ Windows 11, Ryzen i7 5800x3d, nvidia 3080 12 Gb



## Test protocol

During the testing I would film in slow-mo the HMD lenses, PC screen and the HMD controller in view and then flick the controller to induce movement. Repeat that 10-20 times.

Afterwards I would extract the frames as jpeg files, go frame by frame and note the frame number when the controller apparently started moving, and the frame when HMD displays turned red.
Pico 4 had a little paper slip over the IR detector to prevent it from going to sleep.

Difference of frame numbers between movement start and HMD going red divided by 120 is my latency in seconds.
I've calculated mean per HMD and standard deviation of the mean for that mean.

Overall errorbar is the 1/120 - slow mo video framerate + standard deviation of the mean, to include the fact I can easily misjudge start of the movement by a frame.

Example flicks to demonstrate the delays and methodology:




https://github.com/user-attachments/assets/bb43a5e6-a509-4fac-9d59-a4d4b40f3f62

## Uncertainty calculation

We're calculating the latency as the mean of measured delays per HMD. Uncertainty would be the standard deviation of the mean:

$\sigma_m = \frac{\sigma_{total}}{\sqrt{N}}$

Where N is amount of measurements.

$\sigma_{total}$ is a combination of two uncertainties, uncertainty of the instrument - which is dependent on the FPS of the slow motion video, and is usually a half of the minimum interval of the measurement device:

$\sigma_{instrument} = \frac{\frac{1}{{FPS}}}{2}$

At 120 FPS it would be 4.2 ms.

Second uncertainty is coming from the fact that flicks are coming from a random point in time - not aligned with the FPS of the camera and the fact that sometimes I can select earlier or later frame, because start of the motion is that obvious. That we calculate empirically - post factum from the standard deviation of the sample:

$\sigma_{std} = STDEV_{calc function}$

The standard deviations of the measurements are combined by the well known quadratic mean formula:

$\sigma_{total} = \sqrt{\sigma_{instrument}^2 + \sigma_{std}^2}$

Therefore we can calculate the standard deviation of the mean:

$\sigma_m = \frac{\sigma_{total}}{\sqrt{N}}$

Which also decreases with amount of measurements - even though our time ruler is coarse, if we repeat measurements and get very close results, we can be more and more sure about it's mean.


# Results

| HMD                                        | latency [ms] | Standard deviation of the mean including Instrumental uncertainty and Standard deviation of measurements |
| ------------------------------------------ | ------------ | -------------------------------------------------------------------------------------------------------- |
| Vive Pro 2 @ 90 Hz                         | 41.7         | 1.6                                                                                                      |
| OG Vive @ 90 Hz                            | 43.3         | 2.0                                                                                                      |
| Pico 4 standalone @ 90 Hz                  | 49.2         | 2.1                                                                                                      |
| Pico 4 wifi 90 Hz 50 Megabits              | 57.6         | 2.0                                                                                                      |
| Pico 4 wifi 90 Hz 50 Megabits Noisy scene  | 69.9         | 1.6                                                                                                      |
| Pico 4 wifi 90 Hz 130 Megabits Noisy scene | 80.2         | 1.5                                                                                                      |


![results springer](./delays_fixed.png)

Interestingly, Vive Pro 2 at 90 Hz has a similar delay as Valve Index at 90 Hz (from the Springer study), but the OG Vive now has over 10 ms longer delay.
Differences in nvidia drivers? SteamVR? Setting? Between current year (late 2024) VR setups and September 2022 of the Springer study?
Also my methodology is less exact than the one in the study, as I do not have a 240 FPS slow mo camera or a robotic vice to move the controllers.

# Conclusions

As expected, Wireless VR headset have a considerably higher motion to photon latency than wired VR headsets,
at a sensible bit-rate and complex scene almost double that of the wired headsets (40 ms to 80 ms increase of latency).

This can explain the trouble players experience in fast paced shooting games, where they feel less accurate using wireless headset compared to wired:
the gun can move with almost 100 ms delay which is quite noticable. And also overall "sluggish" feel of WiFi compressed video VR headsets.

# Data availability

All the slow-motion videos are available here: `https://drive.google.com/drive/folders/1bhfLbrglGQj0n7F0kcaEFNy4eD3sFgRU?usp=sharing`
You are welcome to recalculate the delays if you are so inclined.

All the calculation are performed in https://github.com/Greendayle/VR-Motion-to-photon-latency-/raw/refs/heads/main/delays.ods which also has some Pico Connect debug screenshots.

# Invitation to repeat the study

I invite everyone with slow-mo capable cameras to go to my world and repeat the study and count the frames between controller movement and HMD lenses changing colors. I am interested how other
wireless HMDs handle that, how better WiFi setups handle the delay, and also different software: ALVR, Virtual Desktop, Steam Link. It's also interesting how much does their debug overall latency estimator misses the real world empirical measurement.

Good luck! You can always send me an issue or a PR.


# Collaboration results

We got some volunteers to measure their delays!

Details about each test are in the [`delays_collab.ods`](https://github.com/Greendayle/VR-Motion-to-photon-latency-/raw/refs/heads/main/delays_collab.ods) file.

VR controller motion to photon latency.
Desktop entries are in analogue to VR, but instead of flicking the controller, we'd flick a mouse.
Almost all entries are made in VRChat world. A few entries have their own proprietary low level OpenXR app.

After discussion with original authours of `https://link.springer.com/content/pdf/10.3758/s13428-022-01983-5.pdf` we realized, that our map can be sampling slightly too old controller pose, and that could explain 1 frame difference in results between OG Vive and Index in the `https://link.springer.com/content/pdf/10.3758/s13428-022-01983-5.pdf` and ours study. A modified version was made, which instead of doing the work in Update() event, does it in the "PostLateUpdate" event, which VRChat documantation claims to `Fired near the end of the frame after IK has been calculated. Getting bone positions at this time will give you the most up to date positions so that they are not a frame behind.`. That improved delay but not by a full frame.

Additionally a custom made low level minimal OpenXR application was provided which tries to do the same test, but makes sure there is no buffering of extra frames or anything like that. That app did reduce the delay, especially in connection with Oculus Link USB connection - using Oculus OpenXR runtime directly, which seems to reduce Quest 2 delay to quite small value of 32 ms, even at 500 megabits (over USB). Which is quite impressive. Althoug the low level application and oculus runtime is now seldom used in VR world, it sets a baseline to which all VR game and runtime/drivers developers should strive for.

| label                                                                                                                                                                  | latency [ms] | Standard deviation of the mean including Instrumental uncertainty and Standard deviation of measurements |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------------- |
| Quest Pro @ 90hz (Linux WIVRN 400Mbps, 3x h265, Noisy) WiFi6 󰚯󰣨󰢔󰻀󱚵󰚽 WiFi6                                                                                        | 999,0        | 0,0                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 200Mbps, 3x x264, Noisy) WiFi6 󰚯󰣨󰢔󰻀󱚵󰚽 WiFi6                                                                                        | 999,0        | 0,0                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 1000Mbps, 3x x264, Noisy) USB3.2Gen1 󰚯󰣨󰢔󰻀󰕓\*󰚽 USB3                                                                                 | 999,0        | 0,0                                                                                                      |
| Pico 4 Pro @ 90hz (Linux ALVR 400Mbps Constant, Noisy) WiFi6 󰚯󰣨󰢔󰓓󱚵 WiFi6                                                                                          | 140,8        | 2,6                                                                                                      |
| Pico 4 Pro @ 90hz (Linux ALVR 200Mbps Constant, Noisy) WiFi6 󰚯󰣨󰢔󰓓󱚵 WiFi6                                                                                          | 137,5        | 2,7                                                                                                      |
| Pico 4 Pro @ 90hz (Linux ALVR 50Mbps Constant, Noisy) WiFi6 󰚯󰣨󰢔󰓓󱚵 WiFi6                                                                                           | 115,9        | 2,0                                                                                                      |
| Quest Pro @ 90 Hz Knuckles Virtual Desktop h264+ 400 mb Noiseless (VD latency: 50 ms) WiFi 6E                                                                          | 111,9        | 2,4                                                                                                      |
| Pico 4 Pro @ 90hz (Linux ALVR 100Mbps Constant, Noisy) WiFi6 󰚯󰣨󰢔󰓓󱚵 WiFi6                                                                                          | 111,6        | 2,3                                                                                                      |
| Quest Pro @ 90 Hz Knuckles Virtual Desktop h264+ 400 mb Noise (VD latency: 60 ms) WiFi 6E                                                                              | 101,8        | 3,1                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 200Mbps, 3x h265, Noisy) WiFi6 󰚯󰣨󰢔󰻀󱚵 WiFi6                                                                                          | 101,3        | 1,8                                                                                                      |
| Quest Pro @ 90 Hz Knuckles Virtual Desktop HEVC 150 Mb Noise (VD latency: 50 ms) WiFi 6E                                                                               | 96,8         | 3,8                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 100Mbps, 3x h265, Noisy) WiFi6 󰚯󰣨󰢔󰻀󱚵 WiFi6                                                                                          | 96,6         | 1,9                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 200Mbps, 3x h265, Noisy) USB3.2Gen1 󰚯󰣨󰢔󰻀󰕓\* USB3                                                                                    | 93,5         | 3,3                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 100Mbps, 3x x264, Noisy) WiFi6 󰚯󰣨󰢔󰻀󱚵 WiFi6                                                                                          | 92,1         | 2,7                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 50Mbps, 3x x264, Noisy) WiFi6 󰚯󰣨󰢔󰻀󱚵 WiFi6                                                                                           | 91,3         | 2,1                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 50Mbps, 3x h265, Noisy) WiFi6 󰚯󰣨󰢔󰻀󱚵 WiFi6                                                                                           | 89,6         | 3,4                                                                                                      |
| Quest 3 @ 90 Hz Knuckles Virtual Desktop HEVC 150 mb Noise (VD latency: 49 ms) WiFi 6E                                                                                 | 87,1         | 2,6                                                                                                      |
| Quest Pro @ 90 Hz Knuckles Virtual Desktop h264+ 150 mb Noiseless (VD latency: 38 ms) WiFi 6E                                                                          | 84,7         | 2,2                                                                                                      |
| Quest 3 @ 90 Hz Knuckles Virtual Desktop h264+ 150 mb Noise (VD latency: 49 ms) WiFi 6E                                                                                | 82,8         | 3,1                                                                                                      |
| Quest Pro @ 90hz (Win10 SteamLink 350Mbps, Noiseless) WiFi6 󰚯󰍲󰢔󰓓󰖩 WiFi6                                                                                           | 82,8         | 2,7                                                                                                      |
| Quest 3 @ 90 Hz Knuckles Virtual Desktop HEVC 150 mb Noiseless (VD latency: 49 ms) WiFi 6E                                                                             | 82,7         | 1,8                                                                                                      |
| Pico 4 Pro @ 90hz (Linux ALVR 50Mbps Constant, Noiseless, w/ script) WiFi6 󰚯󰣨󰢔󰓓󰖩 WiFi6                                                                            | 81,9         | 2,5                                                                                                      |
| Quest Pro @ 90 Hz Knuckles Virtual Desktop HEVC 150 Mb Noiseless (VD latency: 40 ms) WiFi 6E                                                                           | 81,1         | 3,6                                                                                                      |
| Quest Pro @ 90 Hz Knuckles Virtual Desktop h264+ 150 mb Noise (VD latency: 49 ms) WiFi 6E                                                                              | 81,0         | 8,2                                                                                                      |
| Pico 4 Pico Connect, UltraHD wifi 90 Hz 130 Megabits Noisy scene WiFi                                                                                                  | 80,2         | 1,5                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 50Mbps, 3x h265, Noiseless) WiFi6 󰚯󰣨󰢔󰻀󰖩 WiFi6                                                                                       | 79,8         | 2,1                                                                                                      |
| Pico 4 @ 90 Hz, Pico Connect UltraHD h264 300 Megabits Noisy USB2.0                                                                                                    | 78,5         | 2,3                                                                                                      |
| Quest 3 @ 90 Hz Knuckles Virtual Desktop h264+ 150 mb Noiseless (VD latency: 38 ms) WiFi 6E                                                                            | 74,4         | 1,7                                                                                                      |
| Quest Pro @ 90hz (Win10 SteamLink 350Mbps, Noisy) WiFi6 󰚯󰍲󰢔󰓓󱚵 WiFi6                                                                                               | 74,2         | 3,2                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 50Mbps, 3x x264, Noiseless) WiFi6 󰚯󰣨󰢔󰻀󰖩 WiFi6                                                                                       | 74,2         | 1,8                                                                                                      |
| Quest 3, Quest 3 Controllers, VD, 120fps, h265, 10bit, 200mbit, buffer, noisy󰢔󰓓 󱚵󰍲󰚯 WiFi6e                                                                        | 73,8         | 2,2                                                                                                      |
| Quest 3, Quest 3 Controllers, VD, 120fps, h264, 200mbit, no buffer, constant 󰢔󰓓󰖩󰍲󰚯 WiFi6e                                                                         | 70,2         | 2,3                                                                                                      |
| Pico 4 Pico Connect UltraHD wifi 90 Hz 50 Megabits Noisy scene WiFi                                                                                                    | 69,9         | 1,6                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 1000Mbps, 3x x264, Noiseless) USB3.2Gen1 󰚯󰣨󰢔󰻀󰕓 USB3                                                                                 | 68,3         | 1,7                                                                                                      |
| Quest 3, Quest 3 Controllers, VD, 120fps, h264, 200mbit, buffer, noisy 󰢔󰓓 󱚵󰍲󰚯 WiFi6e                                                                              | 68,3         | 3,0                                                                                                      |
| Quest 3, Quest 3 Controllers, Steamlink, 120fps, 350mbit, max res, noise 󰢔󰓓󱚵󰍲󰚯 WiFi6e                                                                             | 66,7         | 2,9                                                                                                      |
| Pico 4 @ 90 Hz, Pico Connect UltraHD h264 300 Megabits Noiseless USB2.0                                                                                                | 66,7         | 2,6                                                                                                      |
| Pico 4 @ 90 Hz, Pico Connect UltraHD h264 50 Megabits Noisy USB2.0                                                                                                     | 64,7         | 1,8                                                                                                      |
| Quest 3, Quest 3 Controllers, VD, 120fps, h264, 200mbit, no buffer, noisy 󰢔󰓓 󱚵󰍲󰚯 WiFi6e                                                                           | 64,4         | 1,7                                                                                                      |
| Quest Pro @ 90hz (Linux WIVRN 200Mbps, 3x h265, Noiseless) USB3.2Gen1 󰚯󰣨󰢔󰻀󰕓 USB3                                                                                  | 64,2         | 2,6                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux Envision MS_0) DP1.4 󰚯󰣨󰢔󰻀󰡁 DP1.4                                                                                                   | 62,9         | 1,3                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux SteamVR) DP1.4 – PostLateUpdate Map 󰚯\*󰣨󰢔󰓓󰡁 DP1.4                                                                                  | 61,6         | 2,1                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux Envision) DP1.4 󰚯󰣨󰢔󰻀󰡁 DP1.4                                                                                                        | 61,1         | 0,9                                                                                                      |
| Pico 4 @ 90 Hz, Pico Connect UltraHD h264 50 Megabits Noiseless USB2.0                                                                                                 | 60,9         | 1,6                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux Envision APP0 COMP-3) DP1.4 󰚯󰣨󰢔󰻀󰡁 DP1.4                                                                                            | 60,6         | 1,4                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux Envision MS_10) DP1.4 󰚯󰣨󰢔󰻀󰡁 DP1.4                                                                                                  | 60,3         | 1,1                                                                                                      |
| Quest 3, Quest 3 Controllers, Steamlink, 120fps, 200mbit, max res, noise 󰢔󰓓󱚵󰍲󰚯 WiFi6e                                                                             | 60,2         | 1,2                                                                                                      |
| Quest 3, Quest 3 Controllers, Steamlink, 120fps, default, constant 󰢔󰓓󰖩󰍲 WiFi6                                                                                      | 58,5         | 1,6                                                                                                      |
| Quest 3, Quest 3 Controllers, Steamlink, 120fps, 200mbit, max res, constant 󰢔󰓓󰖩󰍲󰚯 WiFi6e                                                                          | 58,3         | 2,0                                                                                                      |
| Pico 4 Pico Connect UltraHD wifi 90 Hz 50 Megabits WiFi                                                                                                                | 57,6         | 2,0                                                                                                      |
| Vive Pro Wireless 90 Hz Noisy Scene WiGig                                                                                                                              | 53,8         | 1,1                                                                                                      |
| Bigscreen Beyond @ 75hz (Win10 SteamVR) DP1.4 󰚯󰍲󰢔󰓓󰡁 DP1.4                                                                                                         | 51,1         | 1,3                                                                                                      |
| Pico 4 @ 90 Hz, Pico Connect res: Smooth h264 50 Megabits Noiseless USB2.0                                                                                             | 50,6         | 2,3                                                                                                      |
| Vive Pro Wireless 90 Hz WiGig                                                                                                                                          | 49,6         | 0,7                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux SteamVR) DP1.4 󰚯󰣨󰢔󰓓󰡁 DP1.4                                                                                                         | 49,5         | 1,1                                                                                                      |
| Pico 4 standalone @ 90 Hz eDP?                                                                                                                                         | 49,2         | 2,1                                                                                                      |
| Bigscreen Beyond @ 75 Hz DP                                                                                                                                            | 49,0         | 1,0                                                                                                      |
| PSVR 2 @ 120 Hz PSVR2 controllers DP                                                                                                                                   | 47,4         | 2,7                                                                                                      |
| Bigscreen Beyond @ 90hz (Win10 SteamVR) DP1.4 󰚯󰍲󰢔󰓓󰡁 DP1.4                                                                                                         | 46,1         | 1,3                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux Envision) DP1.4 – Terry App 󰠖󰣨󰢔󰻀󰡁 DP1.4                                                                                            | 45,8         | 2,6                                                                                                      |
| Bigscreen Beyond @ 90 Hz DP                                                                                                                                            | 44,2         | 0,8                                                                                                      |
| Valve Index @ 120hz (Win10 SteamVR) DP1.2 󰚯󰍲󰢔󰓓󰡁 DP1.2                                                                                                             | 43,8         | 1,5                                                                                                      |
| OG Vive @ 90 Hz DP                                                                                                                                                     | 43,3         | 2,0                                                                                                      |
| Quest 2 @ 120 Hz Virtual Desktop, SteamVR, h264, 150mbps, ultra. VD latency 30ms. CUSTOM SELF MADE LOW LEVEL ENGINELESS PROPRIETARY OPENXR APPLICATION, 2688x2784 WiFi | 42,7         | 2,4                                                                                                      |
| Vive Pro 2 @ 90 Hz DP                                                                                                                                                  | 41,7         | 1,6                                                                                                      |
| Vive Pro 2 @ 90 Hz CUSTOM SELF MADE LOW LEVEL ENGINELESS PROPRIETARY OPENXR APPLICATION DP                                                                             | 41,7         | 2,4                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux SteamVR w/ script) DP1.4 󰚯󰣨󰢔󰓓󰡁 DP1.4                                                                                               | 41,7         | 1,0                                                                                                      |
| Valve Index @ 144hz (Linux Envision) DP1.2 󰚯󰣨󰢔󰻀󰡁 DP1.2                                                                                                            | 40,4         | 1,2                                                                                                      |
| PSVR 2 @ 120 Hz Index controllers DP                                                                                                                                   | 40,1         | 2,6                                                                                                      |
| Vive Pro 2 @ 90 Hz postlateupdate DP                                                                                                                                   | 37,5         | 2,0                                                                                                      |
| Valve Index @ 144hz (Win10 SteamVR) DP1.2 󰚯󰍲󰢔󰓓󰡁 DP1.2                                                                                                             | 37,1         | 1,6                                                                                                      |
| Vive Pro 2 @ 120 Hz DP                                                                                                                                                 | 36,3         | 1,9                                                                                                      |
| Valve Index @ 144hz (Linux SteamVR) DP1.2 󰚯󰣨󰢔󰓓󰡁 DP1.2                                                                                                             | 35,3         | 1,3                                                                                                      |
| Desktop G502 Hero, VQ248QE Asus 144hz DP                                                                                                                               | 35,2         | 1,5                                                                                                      |
| Desktop Logitech G305, iiyama G-Master GE2288HS 75 Hz DP                                                                                                               | 34,3         | 1,8                                                                                                      |
| Bigscreen Beyond @ 90hz (Linux SteamVR) DP1.4 – Terry App 󰠖󰣨󰢔󰓓󰡁 DP1.4                                                                                             | 33,3         | 5,0                                                                                                      |
| Vive Pro 2 @ 120 Hz postlateupdate DP                                                                                                                                  | 32,1         | 1,8                                                                                                      |
| Quest 2 @ 120 Hz Quest controllers, oculus OpenXR runtime, USB,CUSTOM SELF MADE LOW LEVEL ENGINELESS PROPRIETARY OPENXR APPLICATION , 500 Mb 2704x2736, noiseless USB3 | 32,1         | 1,4                                                                                                      |
| Quest 2 @ 120 Hz Quest controllers, oculus OpenXR runtime, USB,CUSTOM SELF MADE LOW LEVEL ENGINELESS PROPRIETARY OPENXR APPLICATION , 500 Mb 2704x2736, noisy USB3     | 31,3         | 2,3                                                                                                      |
| Vive Pro 2 @ 120 Hz CUSTOM SELF MADE LOW LEVEL ENGINELESS PROPRIETARY OPENXR APPLICATION DP                                                                            | 26,2         | 2,0                                                                                                      |
| LG 27GP950-B @ 144hz (Linux, Sway (Wayland)) DP1.4 󰚯󰣨󱨜󰹑󰡁 DP1.4                                                                                                    | 19,5         | 2,0                                                                                                      |


󰢔󰓓 - SteamVR/ALVR/SteamLink

󰢔󰻀 - Envision/Monado/OpenComposite/WIVRN

󰚯 - Vrchat Map; * denotes PostLateUpdate version

󰠖 - OpenXR lightweight standalone app

󰖩 - Wireless Noiseless Scene

󱚵 - Wireless Noisy Scene

󰕓 - Wired Streaming (USB); * denotes Noisy scene

󰍲 - Windows 10

󰡁 - Wired DisplayPort/HDMI

󱨜󰹑 - Desktop

󰚽 - DNF; denotes heavy desync in footage, input lag, packet loss, unplayable state, etc.

![image](https://github.com/user-attachments/assets/1ba3f0cf-58b4-4447-a93e-8fb6fe14a3d8)


![results collab](./delays_collab.jpg)

Differently sorted:

![results collab](./delays_collab_sorted_by_hmd.jpg)

Raw video is available here https://drive.google.com/drive/u/2/folders/1bhfLbrglGQj0n7F0kcaEFNy4eD3sFgRU

## Collaborators
+ Greendayle
+ Anonymous
+ spiritmarsrover
+ just_rocs
+ Anonymous
+ Anonymous

## Collaboration conclusions
Wired headsets:
+ 90 Hz baseline is 40 ms
+ are slighly slower than connected monitors showing the game window?
+ Vive Wireless adds around 10 ms, resulting around 50 ms total, which kinda makes sense, as there must be a frame buffer somewhere?

Wifi connected headsets:
+ at 50 megabits, which looks pretty bad, you can get near the vive pro wireless delay, but still 10-20 ms slower (57-70 ms overall, depending on scene complexity)
+ at around 150 megabits, which looks better, you get around 80 ms delay - double that to display port connected headset
+ at 400 megabits when compression artifacts start to be less noticable you get 110 ms delay, which is quite a lot, explains why people report that they are less accurate in shooter games
+ faster wifi does not help with latency, but allows higher video bandwith at a cost of latency
+ Pico Connect seems to be as good as Virtual Desktop at equivalent bitrates and video encoders, latency wise. Makes sense as all our collaborators use NVIDIA video cards, Pico Connect and Virtual Desktop use the same GPU hardware encoders, and both Pico and Quest are XR2 devices with the same decoders.
+ virtual desktop "total delay" seems to be missing 40 ms compared to full motion to photon delay.
+ Using USB cable shouldn't change the total delay dramatically, but might reduce some of the transmission delay.

Linux:
+ opensource Monado and ALVR linux VR stack seems to have quite more latency on wired and wifi headsets, like there are 2-3 frames delay added.

Overall:
+ steam vr/vrchat might be adding 1-2 frames frame buffer. Low level direct OpenXR apps can reduce latency!
+ Carmack is god and helped to create an amazing VR runtime which can slash 10-20 ms off the baseline.
+ Current VR games and SteamVR runtime seems to have additional frame buffers causing unnecesary delay. Unperceptable on cable, but on high bitrate, high resolution WiFi connection if starts to give.

