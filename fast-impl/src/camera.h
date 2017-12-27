#ifndef _CAMERA_H_
#define _CAMERA_H_

#include <Argus/Argus.h>
#include <gst/gst.h>
#include <stdlib.h>
#include <unistd.h>
#include "Error.h"
#include "Options.h"
#include "PreviewConsumer.h"

namespace Camera {
    using namespace Argus;
    static const int32_t    FRAMERATE   = 30;
    static const int32_t    BITRATE     = 14000000;
    static const uint32_t   DEFAULT_CAMERA_INDEX = 0;

    struct cameraOptions {
        uint32_t            cameraIndex;
        int32_t             framerate;
    };

    class CSICam {
    private:
        cameraOptions           options;
        ICameraProvider         *iCameraProvider;
        ICameraProperties       *iCameraProperties;
        ICaptureSession         *iSession;
        ISensorMode             *iSensorMode;
        IOutputStreamSettings   *iStreamSettings;
        IStream                 *iVideoStream;
        IStream                 *iPreviewStream;
        IRequest                *iRequest;
    public:
        CSICam(cameraOptions &options);
        ~CSICam();

        EGLStreamKHR        getEGLStream();
        Size2D<uint32_t>    getResolution();
        bool                initialize();
    };
}

#endif
