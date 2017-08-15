//
//  test_v2.cpp
//  TestOpenCV
//
//  Created by Nghia Nguyen on 7/13/17.
//  Copyright © 2017 Nghia Nguyen. All rights reserved.
//

#include "extract_cell.hpp"
#include "constants.hpp"
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

/* Important threshold*/
const int HOUGH_LINE_THRESHOLD = 1000;
/* End of threshold */

/* Debug purpose */
#define ENABLE_REMOVE_BORDER 1


std::string INPUT_FILE_NAME_OPTION = "--inputFileName";
std::string OUTPUT_FOLDER_OPTION = "--outputFolder";
std::string DEBUG_OPTION = "--debug";

bool isBorderLine(const Mat& outerBox, int x1, int y1, int x2, int y2, int threshold) {
    int cnt = 0;
    for(int y = y1; y <= y2; ++y) {
        const uchar *row = outerBox.ptr(y);
        for (int x = x1; x <= x2; ++x) {
            if (row[x] == 255) {
                ++cnt;
                if (cnt >= threshold) return true;
            }
        }
    }
    return false;
}

void getCellBorder(const Mat& outerBox, double percent_threshold, Point& cp1, Point& cp2){
    int n = outerBox.size().width - 1;
    int m = outerBox.size().height - 1;
    int x = n / 2;
    int y = m / 2;
    //Move left
    int xLeft = x;
    while(xLeft > 0) {
        if (isBorderLine(outerBox, xLeft, 0, xLeft, m, percent_threshold * m)) {
            break;
        }
        xLeft--;
    }
    xLeft++;

    //Move right
    int xRight = x;
    while(xRight < n) {
        if (isBorderLine(outerBox, xRight, 0, xRight, m, percent_threshold * m)) {
            break;
        }
        xRight++;
    }
    xRight--;

    //Move up
    int yUp = y;
    while(yUp > 0) {
        if (isBorderLine(outerBox, 0, yUp, n, yUp, percent_threshold * n)) {
            break;
        }
        yUp--;
    }
    yUp++;
    //Move down
    int yDown = y;
    while(yDown < m) {
        if (isBorderLine(outerBox, 0, yDown, n, yDown, percent_threshold * n)) {
            break;
        }
        yDown++;
    }
    yDown--;
    cp1.x = xLeft + 1;
    cp1.y = yUp + 1;

    cp2.x = xRight - 1;
    cp2.y = yDown - 1;
}


void findCells(vector<Vec2f>& lines, Mat& img, int numRow, const std::string& inputFileName, const std::string& outputFolder) {
    Point2f src[4], dst[4];
    double maxLength = findExtremeLines(lines, img, src, dst);
    Mat original_img = imread(inputFileName, 0);
    Mat undistorted ;
    cv::warpPerspective(original_img, undistorted, cv::getPerspectiveTransform(src, dst), Size(maxLength, maxLength));
    imwrite(outputFolder + "/undistorted.jpg", undistorted);
    //vector<double> p = {1, 1, 1, 2, 1, 1, 1};
    vector<double> p = {2, 2, 6, 6, 4, 2, 2,     2, 2, 6, 6, 4, 2, 2};
    
    double sum = 0;
    double gap = maxLength / numRow;
    for(int i = 0; i < p.size(); ++i) {
        sum += p[i];
    }
    double halfLineGap = 0.08   *  maxLength / sum;
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
            p0.x = p1.x;
            char st[100];
            std::string fileName = outputFolder + "/file%lu.png";
            sprintf(st, fileName.c_str(), i * p.size() + j);
        
            Mat outerBox = Mat(img.size(), CV_8UC1);
            Mat kernel = (Mat_<uchar>(3,3) << 0,1,0,1,1,1,0,1,0);
            preprocessing_cell(miniMat, outerBox, kernel);

            #if ENABLE_REMOVE_BORDER 
                Point cp1, cp2;
                getCellBorder(outerBox, 0.8, cp1, cp2);

                cv::Rect inside(cp1, cp2);
                outerBox = outerBox(inside);
            #endif
            imwrite(st, outerBox);
        }
    }
    
}

void detectLine(Mat& outerBox, Mat& img, vector<Vec2f>& lines){
    HoughLines(outerBox, lines, 1, CV_PI/180, HOUGH_LINE_THRESHOLD);
    for(int i=0;i<lines.size();i++) {
        drawLine(lines[i], outerBox, CV_RGB(255,255,255));
    }
    printf("Number of lines found %lu\n", lines.size());
    mergeRelatedLines(&lines, outerBox);
    printf("Number of lines after merged %lu\n", lines.size());
}

char* getCmdOption(char ** begin, char ** end, const std::string & option)
{
    char ** itr = std::find(begin, end, option);
    if (itr != end && ++itr != end)
    {
        return *itr;
    }
    return 0;
}

bool cmdOptionExists(char** begin, char** end, const std::string& option)
{
    char ** itr =  std::find(begin, end, option);
    return itr != end && (++itr) != end;
}

int main(int argc, char** argv)
{
    if (!cmdOptionExists(argv, argv + argc, INPUT_FILE_NAME_OPTION)) {
        printf("Input file name option %s does not exist\n", INPUT_FILE_NAME_OPTION.c_str());
        return 0;
    }
    string fileName(getCmdOption(argv, argv + argc, INPUT_FILE_NAME_OPTION));
    printf("Input filename = %s\n", fileName.c_str());

    if (!cmdOptionExists(argv, argv + argc, OUTPUT_FOLDER_OPTION)) {
        printf("Output folder option %s does not exist\n", OUTPUT_FOLDER_OPTION.c_str());
        return 0;
    }
    string outputFolder(getCmdOption(argv, argv + argc, OUTPUT_FOLDER_OPTION));
    printf("Output folder %s\n", outputFolder.c_str());

    Mat img = imread(fileName, 0);
    Mat kernel = (Mat_<uchar>(3,3) << 0,1,0,1,1,1,0,1,0);
    Mat outerBox = Mat(img.size(), CV_8UC1);

    printf("Preprocessing img");
    preprocessing(img,outerBox, kernel);
    imwrite(outputFolder + "/preprocessing.jpg", outerBox);

    printf("Find table blob");
    findTableBlob(outerBox, kernel);
    imwrite(outputFolder + "/findBlob.jpg", outerBox);

    vector<Vec2f> lines;
    detectLine(outerBox, img, lines);

    int numRows = 30;
    findCells(lines, img, numRows, fileName, outputFolder);
}
