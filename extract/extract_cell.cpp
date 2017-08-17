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
#include <iostream>
#include <vector>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv/cvaux.hpp>

using namespace cv;
using namespace std;

/* Important threshold*/
const int HOUGH_LINE_THRESHOLD = 500;
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
    cp1.x = xLeft + 3;
    cp1.y = yUp + 3;

    cp2.x = xRight - 3;
    cp2.y = yDown - 3;
}

double findDstCorners(Point2f src[4], Point2f dst[4]) {
    double max_len = -1;
    for(int i = 0; i < 4; ++i) {
        int j = (i+1) % 4;
        double len = sqrt(
            (src[i].x - src[j].x) * (src[i].x - src[j].x) + 
            (src[i].y - src[j].y) * (src[i].y - src[j].y) );
        max_len = max(len, max_len);
    }
    dst[0] = Point2f(0, 0);
    dst[1] = Point2f(max_len, 0);
    dst[2] = Point2f(max_len, max_len);
    dst[3] = Point2f(0, max_len);
    return max_len;
}

void findFourCorners(Mat& outerBox, Point2f corner[4]) {
    int xleft = INT_MAX; 
    int xright = -1; 
    int ytop = INT_MAX;
    int ybottom = -1;
    for(int y = 0; y < outerBox.size().height; ++y) {
        const uchar *row = outerBox.ptr(y);
        for (int x = 0; x < outerBox.size().width; ++x) {
            if (row[x] == 255) {
                xleft = min(xleft, x);
                xright = max(xright, x);
                ytop = min(ytop, y);
                ybottom = max(ybottom, y); 
            }
        }
    }
    // pTopLeft, pTopRight, pBottomLeft, pBottomRight;
    Point2f approx[4] = {
        Point2f(xleft, ytop), 
        Point2f(xright, ytop), 
        Point2f(xright, ybottom), 
        Point2f(xleft, ybottom)};
    double d[4] = {DBL_MAX, DBL_MAX, DBL_MAX, DBL_MAX};
    for(int y = 0; y < outerBox.size().height; ++y) {
        const uchar *row = outerBox.ptr(y);
        for (int x = 0; x < outerBox.size().width; ++x) {
            if (row[x] == 255) {
                for(int i = 0; i < 4; ++i) {
                    double y1 = approx[i].y;
                    double x1 = approx[i].x;
                    double dd = (y-y1) * (y-y1) + (x-x1) * (x-x1);
                    if (dd < d[i]) {
                        d[i] = dd;
                        corner[i] = Point(x,y);
                        //cout << "Found " << x << " " << y << endl;
                    }
                }
            }
        }
    }
    #if 0
    for(int i = 0; i < 4; ++i) {
        cv::line(outerBox, corner[i], corner[(i+1) % 4], COLOR);
        cout << "Point = " << corner[i] << endl;
    }
    imshow( "Contours", outerBox);
    waitKey();
    #endif
}

void detectBoundary(const Mat& img, const Point& p, Point& p0, Point& p1) {
    int n = img.size().width - 1;
    int m = img.size().height - 1;
    //Move left
}

void findCells(
    Mat& img, Mat& outerBox, 
    int numRow, 
    const std::string& inputFileName, 
    const std::string& outputFolder) 
 {
    Mat kernel = (Mat_<uchar>(3,3) << 0,1,0,1,1,1,0,1,0);
    Point2f src[4], dst[4];
    findFourCorners(outerBox, src);
    double maxLength = findDstCorners(src, dst);

    Mat original_img = imread(inputFileName, 0);
    Mat undistorted ;
    cv::warpPerspective(original_img, undistorted, cv::getPerspectiveTransform(src, dst), Size(maxLength, maxLength));
    threshold(undistorted, outerBox, GRAY_THRESHOLD, 255, THRESH_BINARY);
    bitwise_not(outerBox, outerBox);
    findTableBlob(outerBox, kernel);
    imwrite(outputFolder + "/outerBox_undistortoed.png", outerBox);
    #if 1 
    bool found = false;
    for(int y=0;y<outerBox.size().height;y++) {
        uchar *row = outerBox.ptr(y);
        for(int x=0;x<outerBox.size().width;x++) {
            if (row[x] != 0 && row[x] != 255) {
                printf("OHNOW %d\n", row[x]);
                found = true;
                break;
            }
        }
        if (found) break;
    }
    #endif 


    imwrite(outputFolder + "/undistorted.jpg", undistorted);
    imwrite(outputFolder + "/undistorted_processed.jpg", outerBox);
    //vector<double> p = {1, 1, 1, 2, 1, 1, 1};
    vector<double> p = {2, 2, 6, 6, 4, 2, 2,  2, 2, 6, 6, 4, 2, 2};
    
    double sum = 0;
    double gap = maxLength / numRow;
    for(int i = 0; i < p.size(); ++i) {
        sum += p[i];
    }
    for(int i = 0; i < numRow; ++i) {
        Point p0, p1;
        p0.x = 0;
        p0.y = i * gap;

        //Skip the black part
        #if 1 
        int r = p0.y;
        // To avoid the full black line on top or bottom
        if (i == 0) {
           r = gap / 2; 
        } else {
           r -= gap / 2;
        }
        const uchar *row = outerBox.ptr(r);
        while(row[p0.x] == 0) {
            //printf("%d %d\n", p0.x, row[p0.x]);
            p0.x++;
        }
        int last_col = outerBox.size().width - 1;
        double newLength = maxLength - p0.x;
        while(row[last_col] == 0) {
            --last_col;
            --newLength;
        }
        #else 
        double newLength = maxLength ;
        #endif 
        double halfLineGap = 0.08   *  newLength / sum;
        printf("row %d value of p0.x = %d\n", i, p0.x);
        p1.y = p0.y + gap;
        for(int j = 0; j < p.size(); ++j) {
            p1.x = p0.x + (((double)p[j]/sum) * (double)newLength) ;
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

            #if 1  // Old way - getting the rect
            Mat miniMat = undistorted(rect);
            //Mat miniMat = outerBox(rect);
            p0.x = p1.x;
            char st[100];
            std::string fileName = outputFolder + "/file%lu.png";
            sprintf(st, fileName.c_str(), i * p.size() + j);
        
            Mat outerBox = Mat(img.size(), CV_8UC1);
            Mat kernel = (Mat_<uchar>(3,3) << 1,1,1,1,1,1,1,1,1);
            preprocessing_cell(miniMat, outerBox, kernel);

                #if ENABLE_REMOVE_BORDER 
                Point cp1, cp2;
                getCellBorder(outerBox, 0.8, cp1, cp2);

                cv::Rect inside(cp1, cp2);
                outerBox = outerBox(inside);
                #endif
            imwrite(st, outerBox);
            #else 
            detectBoundary(
                outerBox, 
                Point((p0.x + p2.x) / 2, (p0.y + p2.y) / 2),
                bp0, bp1);
            #endif
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


void findCellUsingContour(Mat img, Mat outerBox) {
    vector<vector<Point> > contours;
    vector<Vec4i> hierarchy;
    // Find contours
    findContours( outerBox, contours, hierarchy, CV_RETR_LIST, CV_CHAIN_APPROX_SIMPLE);
    printf("Number of contours found %lu\n", contours.size());
    vector<Point>  approx;
    vector<Point> table;
    double max_area = 0.0;
    /// Draw contours
    Mat drawing = Mat::zeros( outerBox.size(), CV_8UC3 );
    for(int i = 0; i < contours.size(); ++i) {
        approxPolyDP(Mat(contours[i]), approx, 4, true);

        if (approx.size() != 4) {
            continue;
        }
        if (!isContourConvex(approx)) {
            continue;
        }
        /*
        for(int i = 0; i < approx.size(); ++i) {
            cv::line(drawing, approx[i], approx[(i+1) % 4], COLOR);
        }*/
        imshow( "Contours", drawing);
        double area = contourArea(approx);
        if (max_area < area) {
            max_area = area;
            table = approx;
        }
    }
  
    waitKey();
    printf("Image width & height :  %d %d\n", outerBox.size().width, outerBox.size().height);
    printf("Largest table:%lf\n", max_area);
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

    int numRows = 30;
    findCells(img, outerBox, numRows, fileName, outputFolder);
}
