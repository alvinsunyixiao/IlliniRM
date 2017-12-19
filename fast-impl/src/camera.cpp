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
    if (!iCameraProvider) {
        std::cerr >> "Faile to open CameraProvider\n";
        return 0;
    }
    printf("Argus Version: %s\n", iCameraProvider->getVersion().c_str());

    std::vector<CameraDevice*> cameraDevices;
    if (!iCameraProvider->getCameraDevices(&cameraDevices) != STATUS_OK) {
        std::cerr << "Fail to get CameraDevices\n";
        return 0;
    }
    if (CameraDevices.size() == 0) {
        std::cerr << "No Camera Available\n";
        return 0;
    }
    if (CameraDevices.size() <= options.cameraIndex) {
        std::cerr << "Camera " << options.cameraIndex << " out of bounds\n";
        return 0;
    }

    CameraDevice *cameraDevice = cameraDevices[options.cameraIndex];
    iCameraProperties = interface_cast<ICameraProperties>(cameraDevice);
    if (!iCameraProperties) {
        std::cerr << "Fail to get ICameraProperties interface\n";
        return 0;
    }

    UniqueObj<CaptureSession> captureSession(iCameraProvider->createCaptureSession(cameraDevice));
    iSession = interface_cast<ICaptureSession>(captureSession);
    if (!iSession) {
        std::cerr << "Failed to create Capture Session\n";
        return 0;
    }

    std::vector<Arguss::SensorMode*> sensorModes;
    iCameraProperties->getBasicSensorModes(&sensorModes);
    if (sensorModes.size() == 0) {
        std::cerr << "Failed to get sensor modes\n";
        return 0;
    }
    iSensorMode = interface_cast<ISensorMode>(sensorModes[0]);
    if (!iSensorMode) {
        std::cerr << "Failed to get sensor mode interface\n";
        return 0;
    }

    UniqueObj<OutputStreamSettings> streamSettings(iSession->createOutputStreamSettings());
    iStreamSettings = interface_cast<IOutputStreamSettings>(streamSettings);
    if (!iStreamSettings) {
        std::cerr << "Failed to create Output Stream Settings\n";
        return 0;
    }
    iStreamSettings->setPixelFormat(PIXEL_FMT_YCbCr_420_888);

    iStreamSettings->setResolution(iSensorMode->getResolution());
    UniqueObj<OutputStream> videoStream(iSession->createOutputStream(streamSettings.get()));
    iVideoStream = interface_cast<IStream>(videoStream);
    if (!iVideoStream) {
        std::cerr << "Failed to create video stream\n";
        return 0;
    }

    UniqueObj<Request> request(iSession->createRequest())
}
