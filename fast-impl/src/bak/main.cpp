/*
 * Copyright (c) 2016, NVIDIA CORPORATION. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *  * Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *  * Neither the name of NVIDIA CORPORATION nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
 * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <Argus/Argus.h>
#include <gst/gst.h>
#include <stdlib.h>
#include <unistd.h>
#include "Error.h"
#include "Options.h"
#include "PreviewConsumer.h"
#include "camera.h"

namespace ArgusSamples
{

// Constants.
static const int32_t     FRAMERATE = 30;
static const int32_t     BITRATE   = 14000000;
static const char*       ENCODER   = "omxh264enc";
static const char*       MUXER     = "qtmux";
static const char*       OUTPUT    = "argus_gstvideoencode_out.mp4";
static const uint32_t    DEFAULT_CAPTURE_TIME  = 10; // In seconds.
static const uint32_t    DEFAULT_CAMERA_INDEX = 0;
static const Argus::Rectangle<uint32_t> DEFAULT_WINDOW_RECT(0, 0, 640, 480);
static const Argus::Size2D<uint32_t>    PREVIEW_STREAM_SIZE(640, 480);

// Globals.
EGLDisplayHolder g_display;

/**
 * Class to initialize and control GStreamer video encoding from an EGLStream.
 */
class GstVideoEncoder
{
public:
    GstVideoEncoder()
        : m_state(GST_STATE_NULL)
        , m_pipeline(NULL)
        , m_videoEncoder(NULL)
    {
    }

    ~GstVideoEncoder()
    {
        shutdown();
    }

    /**
     * Initialize the GStreamer video encoder pipeline.
     * @param[in] eglStream The EGLStream to consume frames from.
     * @param[in] resolution The resolution of the video.
     * @param[in] framerate The framerate of the video (in frames per second).
     * @param[in] encoder The encoder to use for encoding. Options include:
     *                    omxh264enc, omxh265enc, omxvp8enc
     * @param[in] muxer The muxer/container to use. Options include:
     *                    qtmux (MP4), 3gppmux (3GP), avimux (AVI), identity (H265)
     * @param[in] output The filename/path for the encoded output.
     */
    bool initialize(EGLStreamKHR eglStream, Argus::Size2D<uint32_t> resolution,
                    int32_t framerate, int32_t bitrate,
                    const char* encoder, const char* muxer, const char* output)
    {
        // Initialize GStreamer.
        gst_init(NULL, NULL);

        // Create pipeline.
        m_pipeline = gst_pipeline_new("video_pipeline");
        if (!m_pipeline)
            ORIGINATE_ERROR("Failed to create video pipeline");

        // Create EGLStream video source.
        GstElement *videoSource = gst_element_factory_make("nveglstreamsrc", NULL);
        if (!videoSource)
            ORIGINATE_ERROR("Failed to create EGLStream video source");
        if (!gst_bin_add(GST_BIN(m_pipeline), videoSource))
        {
            gst_object_unref(videoSource);
            ORIGINATE_ERROR("Failed to add video source to pipeline");
        }
        g_object_set(G_OBJECT(videoSource), "display", g_display.get(), NULL);
        g_object_set(G_OBJECT(videoSource), "eglstream", eglStream, NULL);

        // Create queue.
        GstElement *queue = gst_element_factory_make("queue", NULL);
        if (!queue)
            ORIGINATE_ERROR("Failed to create queue");
        if (!gst_bin_add(GST_BIN(m_pipeline), queue))
        {
            gst_object_unref(queue);
            ORIGINATE_ERROR("Failed to add queue to pipeline");
        }

        // Create encoder.
        m_videoEncoder = gst_element_factory_make(encoder, NULL);
        if (!m_videoEncoder)
            ORIGINATE_ERROR("Failed to create video encoder");
        if (!gst_bin_add(GST_BIN(m_pipeline), m_videoEncoder))
        {
            gst_object_unref(m_videoEncoder);
            ORIGINATE_ERROR("Failed to add video encoder to pipeline");
        }
        g_object_set(G_OBJECT(m_videoEncoder), "bitrate", bitrate, NULL);

        // Create muxer.
        GstElement *videoMuxer = gst_element_factory_make(muxer, NULL);
        if (!videoMuxer)
            ORIGINATE_ERROR("Failed to create video muxer");
        if (!gst_bin_add(GST_BIN(m_pipeline), videoMuxer))
        {
            gst_object_unref(videoMuxer);
            ORIGINATE_ERROR("Failed to add video muxer to pipeline");
        }

        // Create file sink.
        GstElement *fileSink = gst_element_factory_make("filesink", NULL);
        if (!fileSink)
            ORIGINATE_ERROR("Failed to create file sink");
        if (!gst_bin_add(GST_BIN(m_pipeline), fileSink))
        {
            gst_object_unref(fileSink);
            ORIGINATE_ERROR("Failed to add file sink to pipeline");
        }
        g_object_set(G_OBJECT(fileSink), "location", output, NULL);

        // Create caps filter to describe EGLStream image format.
        GstCaps *caps = gst_caps_new_simple("video/x-raw",
                                            "format", G_TYPE_STRING, "I420",
                                            "width", G_TYPE_INT, resolution.width(),
                                            "height", G_TYPE_INT, resolution.height(),
                                            "framerate", GST_TYPE_FRACTION, framerate, 1,
                                            NULL);
        if (!caps)
            ORIGINATE_ERROR("Failed to create caps");
        GstCapsFeatures *features = gst_caps_features_new("memory:NVMM", NULL);
        if (!features)
        {
            gst_caps_unref(caps);
            ORIGINATE_ERROR("Failed to create caps feature");
        }
        gst_caps_set_features(caps, 0, features);

        // Link EGLStream source to queue via caps filter.
        if (!gst_element_link_filtered(videoSource, queue, caps))
        {
            gst_caps_unref(caps);
            ORIGINATE_ERROR("Failed to link EGLStream source to queue");
        }
        gst_caps_unref(caps);

        // Link queue to encoder
        if (!gst_element_link(queue, m_videoEncoder))
            ORIGINATE_ERROR("Failed to link queue to encoder");

        // Link encoder to muxer pad.
        if (!gst_element_link_pads(m_videoEncoder, "src", videoMuxer, "video_%u"))
            ORIGINATE_ERROR("Failed to link encoder to muxer pad");

        // Link muxer to sink.
        if (!gst_element_link(videoMuxer, fileSink))
            ORIGINATE_ERROR("Failed to link muxer to sink");

        return true;
    }

    /**
     * Shutdown the GStreamer pipeline.
     */
    void shutdown()
    {
        if (m_state == GST_STATE_PLAYING)
            stopRecording();

        if (m_pipeline)
            gst_object_unref(GST_OBJECT(m_pipeline));
        m_pipeline = NULL;
    }

    /**
     * Start recording video.
     */
    bool startRecording()
    {
        if (!m_pipeline || !m_videoEncoder)
            ORIGINATE_ERROR("Video encoder not initialized");

        if (m_state != GST_STATE_NULL)
            ORIGINATE_ERROR("Video encoder already recording");

        // Start the pipeline.
        if (gst_element_set_state(m_pipeline, GST_STATE_PLAYING) == GST_STATE_CHANGE_FAILURE)
            ORIGINATE_ERROR("Failed to start recording.");

        m_state = GST_STATE_PLAYING;
        return true;
    }

    /**
     * Stop recording video.
     */
    bool stopRecording()
    {
        if (!m_pipeline || !m_videoEncoder)
            ORIGINATE_ERROR("Video encoder not initialized");

        if (m_state != GST_STATE_PLAYING)
            ORIGINATE_ERROR("Video encoder not recording");

        // Send the end-of-stream event.
        GstPad *pad = gst_element_get_static_pad(m_videoEncoder, "sink");
        if (!pad)
            ORIGINATE_ERROR("Failed to get 'sink' pad");
        bool result = gst_pad_send_event(pad, gst_event_new_eos());
        gst_object_unref(pad);
        if (!result)
            ORIGINATE_ERROR("Failed to send end of stream event to encoder");

        // Wait for the event to complete.
        GstBus *bus = gst_pipeline_get_bus(GST_PIPELINE(m_pipeline));
        if (!bus)
            ORIGINATE_ERROR("Failed to get bus");
        result = gst_bus_poll(bus, GST_MESSAGE_EOS, GST_CLOCK_TIME_NONE);
        gst_object_unref(bus);
        if (!result)
            ORIGINATE_ERROR("Failed to wait for the EOF event");

        // Stop the pipeline.
        if (gst_element_set_state(m_pipeline, GST_STATE_NULL) == GST_STATE_CHANGE_FAILURE)
            ORIGINATE_ERROR("Failed to stop recording.");

        m_state = GST_STATE_NULL;
        return true;
    }

protected:
    GstState m_state;
    GstElement *m_pipeline;
    GstElement *m_videoEncoder;
};


struct ExecuteOptions
{
    uint32_t cameraIndex;
    uint32_t captureSeconds;
    Argus::Rectangle<uint32_t> windowRect;
    bool enablePreview;
};

static bool execute(Camera::CSICam &cam)
{
    using namespace Argus;

    // Initialize the GStreamer video encoder consumer.
    GstVideoEncoder gstVideoEncoder;
    if (!gstVideoEncoder.initialize(cam.getEGLStream(), cam.getResolution(),
                                    FRAMERATE, BITRATE, ENCODER, MUXER, OUTPUT))
        ORIGINATE_ERROR("Failed to initialize GstVideoEncoder EGLStream consumer");
    if (!gstVideoEncoder.startRecording())
        ORIGINATE_ERROR("Failed to start video recording");

    // Perform repeat capture requests for requested number of seconds.
    if (!cam.start())
        ORIGINATE_ERROR("Failed to start repeat capture requests");
    sleep(10);

    cam.stop();
    // Stop video recording.
    if (!gstVideoEncoder.stopRecording())
        ORIGINATE_ERROR("Failed to stop video recording");
    gstVideoEncoder.shutdown();

    return true;
}
}; // namespace ArgusSamples

int main(int argc, char** argv)
{
    printf("Executing Argus Sample: %s\n", basename(argv[0]));

    ArgusSamples::Value<uint32_t> cameraIndex(ArgusSamples::DEFAULT_CAMERA_INDEX);
    ArgusSamples::Value<uint32_t> captureTime(ArgusSamples::DEFAULT_CAPTURE_TIME);
    ArgusSamples::Value<Argus::Rectangle<uint32_t> > windowRect(ArgusSamples::DEFAULT_WINDOW_RECT);
    ArgusSamples::Value<bool> enablePreview(true);

    ArgusSamples::Options options(basename(argv[0]));
    options.addOption(ArgusSamples::createValueOption
        ("device", 'd', "INDEX", "Camera index.", cameraIndex));
    options.addOption(ArgusSamples::createValueOption
        ("duration", 's', "SECONDS", "Capture duration.", captureTime));
    options.addOption(ArgusSamples::createValueOption
        ("rect", 'r', "WINDOW", "Window rectangle.", windowRect));
    options.addOption(ArgusSamples::createValueOption
        ("preview", 'p', "[0 or 1]", "Enable preview window.", enablePreview));

    if (!options.parse(argc, argv))
        return EXIT_FAILURE;
    if (options.requestedExit())
        return EXIT_SUCCESS;

    Camera::cameraOptions executeOptions;
    executeOptions.cameraIndex = cameraIndex.get();

    Camera::CSICam mycam(executeOptions);
    mycam.initialize();

    if (!ArgusSamples::execute(mycam))
        return EXIT_FAILURE;

    return EXIT_SUCCESS;
}
