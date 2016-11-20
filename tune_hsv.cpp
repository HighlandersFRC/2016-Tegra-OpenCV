#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <ctype.h>
#include <stdio.h>
#include <iostream>

using namespace std;
using namespace cv;

int main(int argc, char * argv[])
{
    Mat frame;
    unsigned int rc;
    unsigned int i;

    VideoCapture cap(200);

#if 1
    //VideoCapture cap(200);
#else
    for (i = 0; i < 1000; i += 100)
    {
        VideoCapture cap(i);
        rc = cap.isOpened();
        printf ("Camera type %u, rc=%u\n", i, rc);
    }
    return 0;
#endif


    cap >> frame;

    if (frame.empty () )
    {
        printf ("Frame empty!");
        return -1;
    }
    else
    {
        printf ("Frame NOT empty!\n\n");
        printf ("get WID=%lf, HGT=%lf\n", 
            cap.get(CV_CAP_PROP_FRAME_WIDTH),
            cap.get(CV_CAP_PROP_FRAME_HEIGHT));
    }


    //rc = cap.set(CV_CAP_PROP_FOURCC,CV_FOURCC('H','2','6','4'));
    //printf ("Set H264=%u\n", rc);
    rc = cap.set(CV_CAP_PROP_FOURCC,CV_FOURCC('M','J','P','G'));
    printf ("Set MJPG=%u\n", rc);
    rc = cap.set(CV_CAP_PROP_FRAME_WIDTH,1920);
    printf ("Set WID=%u\n", rc);
    rc = cap.set(CV_CAP_PROP_FRAME_HEIGHT,1080);
    printf ("Set HGT=%u\n", rc);
    //rc = cap.set(CV_CAP_PROP_FPS, 30);
    //printf ("Set FPS=%u\n", rc);

    uint hgt = cap.get(CV_CAP_PROP_FRAME_HEIGHT);

    namedWindow("Frame");
    resizeWindow("Frame", 640, 480);

    int f = 0;
    bool rec = true;

    time_t start,end;
    time(&start);
    int counter=0;

    for(int i = 0; i < 4; i++)
    {
        cap >> frame;

        if (frame.empty () )
        {
            printf ("Frame empty!");
            return -1;
        }
        else
        {
            printf ("Frame NOT empty, height = %u!\n\n", hgt);
        }


        if(rec) {
            ostringstream filename;
            filename << "frame" << f << ".png";
            imwrite(filename.str().c_str(),frame);
            f++;
            ellipse( frame, Point( 100, 100 ),Size( 50,50),0, 0,360,Scalar( 0, 0, 255 ),20,8 );
            }
        imshow("Frame",frame);

        time(&end);
        ++counter;
        double sec=difftime(end,start);
        double fps=counter/sec;
        printf("\n%lf fps",fps);

        if(waitKey(30) == 27) break;
        if(waitKey(30) == 'r') rec = !rec;
    }
    return 0;
}
 
