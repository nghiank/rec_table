#include "preprocessing.hpp"


using namespace cv;
using namespace std;

const int INTERMEDIATE_GRAY = 64;

void preprocessing(
    Mat& img, Mat& outerBox, 
    Mat& kernel, 
    int gaussian_size, 
    int adaptiveThresholdSize, 
    int adaptiveThresholdOffset ) 
{
    GaussianBlur(img, img, Size(gaussian_size, gaussian_size), 0);
    // Figure out how to adjust these number?
    adaptiveThreshold(
        img, outerBox, 255, 
        ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, 
        adaptiveThresholdSize, adaptiveThresholdOffset);
    bitwise_not(outerBox, outerBox);
    dilate(outerBox, outerBox, kernel);
}

void preprocessing_cell(Mat& img, Mat& outerBox, Mat& kernel) {
    GaussianBlur(img, img, Size(5,5), 0);
    adaptiveThreshold(img, outerBox, 255, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, 5, 8);
    bitwise_not(outerBox, outerBox);
    erode(outerBox, outerBox, kernel);
}

Point findLargestBlob(cv::Mat& outerBox, double gray_threshold) {
    int max=-1;
    Point maxPt;
    for(int y=0;y<outerBox.size().height;y++) {
        uchar *row = outerBox.ptr(y);
        for(int x=0;x<outerBox.size().width;x++) {
            if(row[x]>=gray_threshold) {
                int area = floodFill(outerBox, Point(x,y), CV_RGB(0,0, INTERMEDIATE_GRAY));
                if(area>max) {
                    maxPt = Point(x,y);
                    max = area;
                }
            }
        }
    }
    return maxPt;
}

void makeOtherBlack(Mat& outerBox, Point& maxPt) {
    for(int y=0;y<outerBox.size().height;y++) {
        uchar *row = outerBox.ptr(y);
        for(int x=0;x<outerBox.size().width;x++) {
            if(row[x]!=0 && row[x]<=GRAY_THRESHOLD) {
                int area = floodFill(outerBox, Point(x,y), CV_RGB(0,0,0));
            }
        }
    }
}

void findTableBlob(Mat& outerBox, Mat& kernel) {
    Point maxPt = findLargestBlob(outerBox);
    cout << "maxPt " << maxPt << endl;
    floodFill(outerBox, maxPt, CV_RGB(255,255,255));
    makeOtherBlack(outerBox, maxPt);

    #if 0 //Debug
    for(int y=0;y<outerBox.size().height;y++) {
        uchar *row = outerBox.ptr(y);
        for(int x=0;x<outerBox.size().width;x++) {
            if (row[x] != 0  && row[x] != 255) {
                printf("OHNOW %d\n", row[x]);
            }
        }
    }
    #endif
}