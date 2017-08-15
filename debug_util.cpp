
#include "debug_util.hpp"
using namespace cv;

void drawLine(Vec2f line, Mat &img, Scalar rgb)
{
    if(line[1]!=0) {
        float m = -1/tan(line[1]);
        float c = line[0]/sin(line[1]);
        cv::line(img, Point(0, c), Point(img.size().width, m*img.size().width+c), rgb);
    }
    else {
        cv::line(img, Point(line[0], 0), Point(line[0], img.size().height), rgb);
    }
}
