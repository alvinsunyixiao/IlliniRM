#include "camera.h"
#include <Argus/Argus.h>
#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include "Error.h"
#include "PreviewConsumer.h"

using namespace Camera;

CSICam::CSICam(cameraOptions &options) {
    this->options = cameraOptions(options);
}

EGLStreamKHR CSICam::getEGLStream() {
    return iVideoStream->getEGLStream();
}

bool CSICam::initialize() {
    UniqueObj<CameraProvider> cameraProvider(CameraProvider::create());
    iCameraProvider = interface_cast<ICameraProvider>(cameraProvider);
    if (!iCameraProvider)
        ORIGINATE_ERROR("Faile to open CameraProvider");
    printf("Argus Version: %s\n", iCameraProvider->getVersion().c_str());

    std::vector<CameraDevice*> cameraDevices;
    if (!iCameraProvider->getCameraDevices(&cameraDevices) != STATUS_OK)
        ORIGINATE_ERROR("Fail to get CameraDevices");
    if (CameraDevices.size() == 0)
        ORIGINATE_ERROR("No Camera Available");
    if (CameraDevices.size() <= options.cameraIndex)
        ORIGINATE_ERROR("Camera %d not available; there are %d cameras",
                        options.cameraIndex, (unsigned)cameraDevices.size());

    CameraDevice *cameraDevice = cameraDevices[options.cameraIndex];
    iCameraProperties = interface_cast<ICameraProperties>(cameraDevice);
    if (!iCameraProperties)
        ORIGINATE_ERROR("Fail to get ICameraProperties interface");

    UniqueObj<CaptureSession> captureSession(iCameraProvider->createCaptureSession(cameraDevice));
    iSession = interface_cast<ICaptureSession>(captureSession);
    if (!iSession)
        ORIGINATE_ERROR("Failed to create Capture Session");

    std::vector<Arguss::SensorMode*> sensorModes;
    iCameraProperties->getBasicSensorModes(&sensorModes);
    if (sensorModes.size() == 0)
        ORIGINATE_ERROR("Failed to get sensor modes");
    iSensorMode = interface_cast<ISensorMode>(sensorModes[0]);
    if (!iSensorMode)
        ORIGINATE_ERROR("Failed to get sensor mode interface");

    UniqueObj<OutputStreamSettings> streamSettings(iSession->createOutputStreamSettings());
    iStreamSettings = interface_cast<IOutputStreamSettings>(streamSettings);
    if (!iStreamSettings)
        ORIGINATE_ERROR("Failed to create Output Stream Settings");
    iStreamSettings->setPixelFormat(PIXEL_FMT_YCbCr_420_888);
    iStreamSettings->setEGLDisplay(EGL_DEFAULT_DISPLAY);

    iStreamSettings->setResolution(iSensorMode->getResolution());
    UniqueObj<OutputStream> videoStream(iSession->createOutputStream(streamSettings.get()));
    iVideoStream = interface_cast<IStream>(videoStream);
    if (!iVideoStream)
        ORIGINATE_ERROR("Failed to create video stream");

    UniqueObj<Request> request(iSession->createRequest(CAPTURE_INTENT_VIDEO_RECORD));
    iRequest = interface_cast<IRequest>(request);
    if (!iRequest)
        ORIGINATE_ERROR("Failed to create Request");
    if (iRequest->enableOutputStream(videoStream.get()) != STATUS_OK)
        ORIGINATE_ERROR("Failed to enable video stream in Request");

    return true;
}

Argus::Size2D<uint32_t> CSICam::getResolution() {
    return iSensorMode->getResolution();
}

bool CSICam::start() {
    return iSession->repeat(iRequest.get()) == STATUS_OK;
}

void CSICam::stop() {
    iSession->stopRepeat();
    iSession->waitForIdle();
}
