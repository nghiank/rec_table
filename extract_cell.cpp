//
//  test_v2.cpp
//  TestOpenCV
//
//  Created by Nghia Nguyen on 7/13/17.
//  Copyright © 2017 Nghia Nguyen. All rights reserved.
//

#include "extract_cell.hpp"
#include "preprocessing.hpp"
#include "line_util.hpp"
#include "debug_util.hpp"
// Example showing how to read and write images
#include <iostream>
#include <vector>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv/cvaux.hpp>

using namespace cv;
using namespace std;

void removeBorder(Mat& img, Mat& outerBox, Mat& kernel) {
    for(int y=0;y<outerBox.size().height;y++) {
        uchar *row = outerBox.ptr(y);
        int     cnt = 0;
        for(int x=0;x<outerBox.size().width;x++) {
            if(row[x]==64) {
                cnt++;
            }
        }
        if (cnt > outerBox.size().width / 2) {
        } else break;
    }
}


void findCells(vector<Vec2f>& lines, Mat& img, int numRow) {
    Point2f src[4], dst[4];
    double maxLength = findExtremeLines(lines, img, src, dst);
    std::string fileName = "/Users/nghiaround/Desktop/c.png";
    Mat img1 = imread(fileName, 0);
    Mat undistorted ;
    cv::warpPerspective(img1, undistorted, cv::getPerspectiveTransform(src, dst), Size(maxLength, maxLength));
    imwrite("/Users/nghiaround/Desktop/undistorted.jpg", undistorted);
    vector<double> p = {1, 1, 1, 2, 1, 1, 1};
    
    double sum = 0;
    double gap = maxLength / numRow;
    for(int i = 0; i < p.size(); ++i) {
        sum += p[i];
    }
    double halfLineGap = 0.083   * maxLength / (2.0*sum);
    for(int i = 0; i < numRow; ++i) {
        Point p0, p1;
        p0.x = 0;
        p0.y = i * gap;
        p1.y = p0.y + gap;
        for(int j = 0; j < p.size(); ++j) {
            p1.x = p0.x + (((double)p[j]/sum) * (double)maxLength) ;
            //extract cell
            
            Point p2;
            p2.x = p1.x + halfLineGap;
            p2.y = p1.y + halfLineGap;
            
            if (i == numRow - 1) {
                p2.y = p1.y;
            }
            if (j == p.size() -1) {
                p2.x = p1.x;
            }
            cv::Rect rect(p0, p2);
            Mat miniMat = undistorted(rect);
            //imshow("miniMat", miniMat);
            //waitKey();
            p0.x = p1.x;
            //if (j>=0)
            {
                char st[100];
                sprintf(st, "/Users/nghiaround/Desktop/file%lu.png",i * p.size() + j);
            
                Mat outerBox = Mat(img.size(), CV_8UC1);
                //adaptiveThreshold(miniMat, outerBox, 255, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, 11, 5);

                Mat kernel = (Mat_<uchar>(3,3) << 0,1,0,1,1,1,0,1,0);
                preprocessing(miniMat, outerBox, kernel);
                //removeBorder(outerBox, outerBox);
                //cvtColor(outerBox, outerBox, cv::COLOR_RGB2GRAY);

                //bitwise_not(outerBox, outerBox);
                imwrite( st, outerBox);
            }
            
        }
    }
    
}

void detectLine(Mat& outerBox, Mat& img){
    vector<Vec2f> lines;
    HoughLines(outerBox, lines, 1, CV_PI/180, 1000);
    for(int i=0;i<lines.size();i++) {
        drawLine(lines[i], outerBox, CV_RGB(255,255,255));
    }
    printf("Number of lines %lu\n", lines.size());
    imshow("original_image", outerBox);
    mergeRelatedLines(&lines, outerBox);
    int numRows = 20;
    findCells(lines, img, numRows);
}

int main(int argc, char** argv)
{
    std::string fileName = "/Users/nghiaround/Desktop/c.png";
    Mat img = imread(fileName, 0);
    printf("Hello world\n");
    Mat kernel = (Mat_<uchar>(3,3) << 0,1,0,1,1,1,0,1,0);
    Mat outerBox = Mat(img.size(), CV_8UC1);
#if true
    preprocessing(img,outerBox, kernel);
    imwrite("/Users/nghiaround/Desktop/preprocessing.jpg", outerBox);
    //imshow("original_image", outerBox);
    findTableBlob(outerBox, kernel);
    imwrite("/Users/nghiaround/Desktop/findBlob.jpg", outerBox);
    //imshow("original_image", outerBox);
    detectLine(outerBox, img);
#endif
    cv::waitKey();
}
