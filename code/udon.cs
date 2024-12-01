
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
