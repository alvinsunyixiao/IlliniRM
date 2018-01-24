/*
 * main.cpp
 *
 *  Created on: Oct 24, 2016
 *      Author: rick
 */

#include <pcl/common/common_headers.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <librealsense/rs.hpp>

#include <iostream>
#include <chrono>

//===================================================================
// Global data
//===================================================================

#define NOISY       3.5		// Remove points past NOISY meters
#define FPS_MILLI   500		// Update fps every 0.5 seconds


// time typdefs for fps
typedef std::chrono::milliseconds                       TIME_IN_MILLI;
typedef std::chrono::duration<double, std::milli>       TIME_DIFF;
typedef std::chrono::high_resolution_clock::time_point  TIME_POINT;


//===================================================================
// Function declarations
//===================================================================


// Creates the window viewer displaying the point cloud
std::shared_ptr<pcl::visualization::PCLVisualizer> createPointCloudViewer( pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr cloud );

// Looks at RS context info
int printRSContextInfo( rs::context *rsContext );

// Configures RS streams
int configureRSStreams( rs::device *rsCamera );

// Prints the FPS info to the viewer
int printTimeLoop( TIME_POINT &t0, TIME_POINT &t1, TIME_POINT &t2,int &frames, int totalframes, double &fps, double &totalfps, std::shared_ptr<pcl::visualization::PCLVisualizer> v );

// Generats the current frames point cloud data
int generatePointCloud( rs::device *dev, pcl::PointCloud<pcl::PointXYZRGB>::Ptr );




//===================================================================
// Main
//===================================================================
int main( int argc, char** argv ) try
{

    int err = -1;

    int const BOOST_WAIT_TIME = 1;

    // Frame Numbers
    int frames      = 0;
    int totalframes = 0;

    // FPS
    double fps      = 0;
    double totalfps = 0;


    // Time Points used for displaying FPS
    TIME_POINT timePoint0;
    TIME_POINT timePoint1;
    TIME_POINT timePoint2;

    timePoint0 = timePoint1 = timePoint2 = std::chrono::high_resolution_clock::now( );


    // ==== Cloud Setup ====
    pcl::PointCloud<pcl::PointXYZRGB>::Ptr              rsCloudPtr( new pcl::PointCloud<pcl::PointXYZRGB> );
    std::shared_ptr<pcl::visualization::PCLVisualizer>  pclVisualizer;


    // Create the PCL viewer/window
    pclVisualizer = createPointCloudViewer( rsCloudPtr );


    //rs::log_to_console( rs::log_severity::warn );

    // Create the RS context and display info about it
    rs::context rsContext;
    printRSContextInfo( &rsContext );

    // Create the RS camera and configure streaming and start the streams
    rs::device * rsCamera = rsContext.get_device( 0 );
    configureRSStreams( rsCamera );


    while( !pclVisualizer->wasStopped( ) )
    {
        // ==== Timing ====
        ++frames;
        ++totalframes;

        err = printTimeLoop( timePoint0, timePoint1, timePoint2, frames, totalframes, fps, totalfps, pclVisualizer );

        if( err != EXIT_SUCCESS )
        {
            std::cout << "Error in printTimeLoop( )\n" << std::endl;
            return err;
        }

        // ==== Data Grab ====
        err = generatePointCloud( rsCamera, rsCloudPtr );
        if( err != EXIT_SUCCESS )
        {
            std::cout << "Error in getFrame( )\n" << std::endl;
            return err;
        }

        // ==== Update Viewer Cloud State and display it ====
        pclVisualizer->updatePointCloud( rsCloudPtr, "sample cloud" );
        pclVisualizer->spinOnce( 1 );


        //boost::this_thread::sleep( boost::posix_time::microseconds( BOOST_WAIT_TIME ) );
    }

    pclVisualizer->close( );
    return EXIT_SUCCESS;
}
catch( const rs::error & e )
{
    std::cerr << "RealSense error calling " << e.get_failed_function( ) << "(" << e.get_failed_args( ) << "):\n    " << e.what( ) << std::endl;
    return EXIT_FAILURE;
}
catch( const std::exception & e )
{
    std::cerr << e.what( ) << std::endl;
    return EXIT_FAILURE;
}



//===================================================================
// Create the viewer window where the point cloud is rendered
//===================================================================
std::shared_ptr<pcl::visualization::PCLVisualizer> createPointCloudViewer( pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr cloud )
{
    // Open 3D viewer and add point cloud
    std::shared_ptr<pcl::visualization::PCLVisualizer> viewer( new pcl::visualization::PCLVisualizer( "LibRealSense PCL Viewer" ) );

    viewer->setBackgroundColor( 0.251, 0.251, 0.251 ); // Floral white 1, 0.98, 0.94 | Misty Rose 1, 0.912, 0.9 |
    viewer->addPointCloud<pcl::PointXYZRGB>( cloud, "sample cloud" );
    viewer->setPointCloudRenderingProperties( pcl::visualization::PCL_VISUALIZER_POINT_SIZE, 1, "sample cloud" );
    viewer->addCoordinateSystem( 1.0 );
    viewer->initCameraParameters( );
    viewer->setShowFPS( false );

    return( viewer );
}



//===================================================================
// provides context info and will exit if no devices
//===================================================================
int printRSContextInfo( rs::context *c )
{
    printf( "There are %d connected RealSense devices.\n", c->get_device_count( ) );
    if( c->get_device_count( ) == 0 )
        throw std::runtime_error( "No device detected. Is it plugged in?" );

    return EXIT_SUCCESS;
}



//===================================================================
// stream config & enabling for device
//===================================================================
int configureRSStreams( rs::device *rsCamera )
{
    std::cout << "Configuring RS streaming " << rsCamera->get_name( ) << "... ";

    rsCamera->enable_stream( rs::stream::depth, rs::preset::best_quality );
    rsCamera->enable_stream( rs::stream::color, rs::preset::best_quality );
    rsCamera->start( );

    std::cout << "RS streaming enabled and running.\n";

    return EXIT_SUCCESS;
}

//===================================================================
// calculates time stats and prints them on the viewer
//===================================================================
int printTimeLoop( TIME_POINT &t0, TIME_POINT &t1, TIME_POINT &t2,
                   int &frames, int totalframes, double &fps,
                   double &totalfps, std::shared_ptr<pcl::visualization::PCLVisualizer> v )
{

    TIME_IN_MILLI zero_ms{0};

    TIME_DIFF fp_ms;
    TIME_DIFF overall;

    fp_ms = overall = zero_ms;

    t2 = std::chrono::high_resolution_clock::now( );
    fp_ms = ( t2 - t1 );

    if( fp_ms.count( ) > FPS_MILLI )
    {
        fps  = frames / fp_ms.count( );
        fps *= 1000.0;
        frames = 0;
        t1 = t2;
    }

    overall     =  ( t2 - t0 );
    totalfps    =  overall.count( );
    totalfps    /= 1000.0;

    if( ( totalframes % 10 ) == 0 )
    {
        char time_buffer[ 8 ], fps_buffer[ 8 ];

        std::stringstream ss;
        sprintf( time_buffer, "%4.2f", totalfps );
        sprintf( fps_buffer, "%4.2f", fps );

        ss << "FPS: " << fps_buffer << "  Total Frames Processed: " << totalframes << "  Time: " << time_buffer;
        v->removeShape( "text", 0 );
        v->addText( ss.str( ), 10, 0, "text" );
    }

    return EXIT_SUCCESS;
}



//===================================================================
// Get the raw data and build the current frames cloud
//===================================================================
int generatePointCloud( rs::device *dev, pcl::PointCloud<pcl::PointXYZRGB>::Ptr rs_cloud_ptr )
{

    // Wait for new frame data
    if( dev->is_streaming( ) )
        dev->wait_for_frames();

    // Retrieve our images
    const uint16_t * depth_image    = ( const uint16_t * )dev->get_frame_data( rs::stream::depth );
    const uint8_t  * color_image    = ( const uint8_t  * )dev->get_frame_data( rs::stream::color );

    // Retrieve camera parameters for mapping between depth and color
    rs::intrinsics depth_intrin     = dev->get_stream_intrinsics( rs::stream::depth );
    rs::extrinsics depth_to_color   = dev->get_extrinsics( rs::stream::depth, rs::stream::color );
    rs::intrinsics color_intrin     = dev->get_stream_intrinsics( rs::stream::color );
    float scale                     = dev->get_depth_scale( );

    // Depth dimension helpers
    int dw  = 0;
    int dh  = 0;
    int dwh = 0;

    dw = depth_intrin.width;
    dh = depth_intrin.height;

    dwh = dw * dh;

    // Set the cloud up to be used
    rs_cloud_ptr->clear( );
    rs_cloud_ptr->is_dense = false;
    rs_cloud_ptr->resize( dwh );

    // Iterate the data space
    // First, iterate across columns
    for( int dy = 0; dy < dh; dy++ )
    {

        // Second, iterate across rows
        for( int dx = 0; dx < dw; dx++ )
        {
            uint i = dy * dw + dx;
            uint16_t depth_value = depth_image[ i ];

            if( depth_value == 0 )
                continue;

            rs::float2 depth_pixel = { (float)dx, (float)dy };
            float depth_in_meters = depth_value * scale;

            rs::float3 depth_point = depth_intrin.deproject( depth_pixel, depth_in_meters );
            rs::float3 color_point = depth_to_color.transform(depth_point);
            rs::float2 color_pixel = color_intrin.project(color_point);

            const int cx = ( int )std::round( color_pixel.x );
            const int cy = ( int )std::round( color_pixel.y );

            static const float nan = std::numeric_limits<float>::quiet_NaN( );

            // Set up logic to remove bad points
            bool depth_fail = true;
            bool color_fail = true;

            depth_fail = ( depth_point.z > NOISY );
            color_fail = ( cx < 0 || cy < 0 || cx > color_intrin.width || cy > color_intrin.height );

            // ==== Cloud Input Pointers ====

            // XYZ input access to cloud
            float *dp_x;
            float *dp_y;
            float *dp_z;

            dp_x = &( rs_cloud_ptr->points[ i ].x );
            dp_y = &( rs_cloud_ptr->points[ i ].y );
            dp_z = &( rs_cloud_ptr->points[ i ].z );

            // RGB input access to cloud
            uint8_t *cp_r;
            uint8_t *cp_g;
            uint8_t *cp_b;

            cp_r = &( rs_cloud_ptr->points[ i ].r );
            cp_g = &( rs_cloud_ptr->points[ i ].g );
            cp_b = &( rs_cloud_ptr->points[ i ].b );

            // ==== Cloud Input Data ====
            // Set up depth point data
            float real_x        = 0;
            float real_y        = 0;
            float real_z        = 0;
            float adjusted_x    = 0;
            float adjusted_y    = 0;
            float adjusted_z    = 0;

            real_x = depth_point.x;
            real_y = depth_point.y;
            real_z = depth_point.z;

            // Adjust point to coordinates
            adjusted_x = -1 * real_x;
            adjusted_y = -1 * real_y;
            adjusted_z = real_z;

            // Set up color point data
            const uint8_t *offset = ( color_image + ( cy * color_intrin.width + cx ) * 3 );

            uint8_t raw_r       = 0;
            uint8_t raw_g       = 0;
            uint8_t raw_b       = 0;
            uint8_t adjusted_r  = 0;
            uint8_t adjusted_g  = 0;
            uint8_t adjusted_b  = 0;

            raw_r = *( offset );
            raw_g = *( offset + 1 );
            raw_b = *( offset + 2 );

            // Adjust color arbitrarily
            adjusted_r = raw_r;
            adjusted_g = raw_g;
            adjusted_b = raw_b;

            // ==== Cloud Point Evaluation ====
            // If bad point, remove & skip
            if( depth_fail || color_fail )
            {
                *dp_x = *dp_y = *dp_z = (float) nan;
                *cp_r = *cp_g = *cp_b = 0;
                continue;
            }

            // If valid point, add data to cloud
            else
            {
                // Fill in cloud depth
                *dp_x = adjusted_x;
                *dp_y = adjusted_y;
                *dp_z = adjusted_z;

                // Fill in cloud color
                *cp_r = adjusted_r;
                *cp_g = adjusted_g;
                *cp_b = adjusted_b;
            }
        }
    }

    return EXIT_SUCCESS;
}








