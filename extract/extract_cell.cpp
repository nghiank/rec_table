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
#include <algorithm>
#include <iostream>
#include <vector>
#include <unordered_set>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv/cvaux.hpp>

using namespace cv;
using namespace std;

/* Important threshold*/
const int HOUGH_LINE_THRESHOLD = 500;
const int CCA_THRESHOLD = 40;
/* End of threshold */

/* Debug purpose */
#define ENABLE_REMOVE_BORDER 1
#define DEBUG 0

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
    //Sweep from left to right
    int xLeft = 0;
    while(xLeft < n / 2) {
        if (!isBorderLine(outerBox, xLeft, 0, xLeft, m, percent_threshold * m)) {
            break;
        }
        xLeft++;
    }

    //Sweep from right to left
    int xRight = n;
    while(xRight > n / 2) {
        if (!isBorderLine(outerBox, xRight, 0, xRight, m, percent_threshold * m)) {
            break;
        }
        xRight--;
    }
    //Sweep from bottom to top
    int yUp = 0;
    while(yUp < m / 2) {
        if (!isBorderLine(outerBox, 0, yUp, n, yUp, percent_threshold * n)) {
            break;
        }
        yUp++;
    } 
    //Sweep from top to bottom
    int yDown = m;
    while(yDown < m / 2) {
        if (!isBorderLine(outerBox, 0, yDown, n, yDown, percent_threshold * n)) {
            break;
        }
        yDown--;
    }
    int sz = 0;
    cp1.x = xLeft + sz;
    cp1.y = yUp + sz;
    cp2.x = xRight - sz;
    cp2.y = yDown - sz;
}

double findDstCorners(Point2f src[4], Point2f dst[4]) {
    double max_len = -1;
    for(int i = 0; i < 4; ++i) {
        int j = (i+1) % 4;
        double len = sqrt(
            (src[i].x - src[j].x) * (src[i].x - src[j].x) + 
            (src[i].y - src[j].y) * (src[i].y - src[j].y) );
        max_len = int(max(len, max_len));
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

bool isBlankCell(const Mat& img) {
    int cnt = 0;
    for(int y=0;y<img.size().height;y++) {
        const uchar *row = img.ptr(y);
        for(int x=0;x<img.size().width;x++) {
            if (row[x] > GRAY_THRESHOLD) {
                cnt++;
                if (cnt > 20) {
                    cout << cnt << endl;
                    return false;
                }
            }
        }
    }
    cout << endl;
    return true;
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
    dilate(outerBox, outerBox, kernel);
    findTableBlob(outerBox, kernel);
    #if 0 
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
    vector<double> p = {1, 4, 3, 3, 1, 1,    1, 4, 3, 3, 1, 1};
    
    int sum = 0;
    printf("Value of maxLength = %lf\n", maxLength);
    double gap = maxLength / numRow;
    for(int i = 0; i < p.size(); ++i) {
        sum += p[i];
    }
    printf("Number of cell per row = %d\n", sum);
    double col_gap = maxLength / (double)sum;
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
            //If this move too far - probably the border in front missing - we need to move back to 0 position
            if (p0.x >= gap / 2) {
                p0.x = 0;
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
        //printf("row %d value of p0.x = %d\n", i, p0.x);
        p1.y = p0.y + gap;
        //We only run first cell for first row 
        int n = (i == 0) ? 1 : sum;
        cout << "New Line-----> p0=" << p0 << endl;
        for(int j = 0; j < n; ++j) {
            char st[100];
            std::string fileName = outputFolder + "/file%lu.png";
            sprintf(st, fileName.c_str(), i * sum + j);
            
            p1.x = p0.x + col_gap;
            //printf("j = %d, p1.x = %d\n", j, p1.x);
            //extract cell
            Point p2;
            p2.x = p1.x + halfLineGap;
            p2.y = p1.y + halfLineGap;
            if (i == numRow - 1) {
                p2.y = p1.y;
            }
            if (j == n - 1) {
                p2.x = p1.x;
            }
            p2.x = std::min(p2.x, int(maxLength) - 1);
            p2.y = std::min(p2.y, int(maxLength) - 1);
            cv::Rect rect(p0, p2);
            Mat raw_box, miniMat;
            try{
                raw_box = undistorted(rect);
                miniMat = outerBox(rect);
                //cout << "Debug rect=" << rect << ", id="<< i * sum + j << endl;
            } catch(cv::Exception) {
                cout << "Exception when getting raw_box and miniMax: rec=" << rect << endl;
                cout << "p0=" << p0 << ", p1=" << p1 << endl;
            }
            #if DEBUG 
            imwrite(string(st) + "_beforeRemoving.png", miniMat);
            #endif
            p0.x = p1.x;
        
            Point cp1, cp2;
            getCellBorder(miniMat, 0.8, cp1, cp2);

            cv::Rect inside(cp1, cp2);
            Mat box_cell;
            try{
                box_cell = raw_box(inside);
            } catch(cv::Exception) {
                cout << "Exception when getting box_cell: rec=" << inside << endl;
            }
            Mat final_box_cell;
            preprocessing_cell(box_cell, final_box_cell, kernel);
            #if DEBUG
            imwrite(string(st) + "_rawBox.png", box_cell);
            #endif
            cout << st << " : ";
            if (!isBlankCell(final_box_cell)) {
                imwrite(st, final_box_cell);
            }
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

std::string getFileName(int i, int j, int sum, const string& outputFolder) {
    char st[100];
    std::string fileName = outputFolder + "/file%lu.png";
    sprintf(st, fileName.c_str(), i * sum + j);
    return string(st);
}

void updateCorner(Point& p0, Point& p1, int y, int x) {
    p0.x = min(p0.x, x);
    p0.y = min(p0.y, y);
    p1.x = max(p1.x, x);
    p1.y = max(p1.y, y);
}

int bfs(int y, int x, const Mat& img, vector<vector<int> >& visit, int currentCnt, Point& p0, Point& p1) {
    visit[y][x] = currentCnt;
    queue<pair<int, int>> q;
    q.push(make_pair(y,x));
    p0.x = INT_MAX;
    p0.y = INT_MAX;
    p1.x = -1;
    p1.y = -1;
    updateCorner(p0, p1, y, x);
    int total = 1;
    int dx[] = {0, 1, 0, -1};
    int dy[] = {-1, 0, 1, 0};
    int m = img.rows;
    int n = img.cols;
    bool valid = true;
    while(!q.empty()) {
        pair<int, int> p = q.front(); q.pop();
        for(int i = 0; i < 4; ++i) {
            int y1 = p.first + dy[i];
            int x1 = p.second + dx[i];
            if (y1<0 || x1<0 || y1==m || x1==n) continue;
            if (visit[y1][x1]!=0) continue;
            if (img.ptr(y1)[x1] != 0 ) continue;
            visit[y1][x1] = currentCnt; q.push(make_pair(y1, x1));
                       updateCorner(p0, p1, y1, x1);
            ++total;
        }
    }
    p0.x = p0.x + 1;
    p0.y = p0.y + 1;
    p1.x = p1.x - 1;
    p1.y = p1.y - 1;
    return valid ? total: 0;
}

void extractDigitSection(
    const Point& p0, const Point& p1, 
    const Mat& fullImage, const Mat& fullImage_number, vector<vector<int> >& visit, int& currentCnt, 
    Mat& digit) {
    int midx = (int)((p0.x + p1.x) / 2);
    int midy = (int)((p0.y + p1.y) / 2);
    double percent = 0.35;
    int minEdge = min(p1.x - p0.x, p1.y - p0.y) *  percent;
    minEdge = minEdge * minEdge;
    int mmax = 0;
    Rect rect;
    //cout << "Looking inside p0="<<p0 << ", p1=" << p1 << endl;
    for(int y = (int)p0.y; y<=(int)p1.y; ++y) {
        const uchar *row = fullImage.ptr(y);
        for(int x = (int)p0.x; x <= (int)p1.x; ++x) {
            //cout <<"visit:" << visit[y][x] << " " << int(row[x]) << endl;
            if (visit[y][x] != 0 || row[x]!=0) continue;
            int dst = (y - midy) * (y - midy) + (x-midx) * (x-midx);
            if (dst > minEdge) continue;
            ++currentCnt;
            Point p2, p3;
            //printf("BFS From here %d %d\n",y,x);
            int total = bfs(y, x, fullImage, visit, currentCnt, p2, p3);
            //cout <<"Total = " << total << endl;
            if (total > mmax) {
                /*p2.x+=2;
                p2.y+=2;
                p3.x-=2;
                p3.y-=2;*/
                rect = Rect(p2, p3);
                mmax = total;
            }
        }
    }
    digit = fullImage_number(rect);
}

int findConnectedComponent(int y, int x, Mat& img, vector<vector<int> >& visit, int component) {
    int dx[] = {0, 1, 0, -1};
    int dy[] = {-1, 0, 1, 0};
    int m = img.rows;
    int n = img.cols;

    visit[y][x] = component;
    queue<pair<int, int> > q;
    q.push(make_pair(y, x));
    int numItems = 1;
    while (!q.empty()) {
        auto v = q.front(); q.pop();
        for(int i = 0; i < 4; ++i) {
            int y1 = v.first + dy[i];
            int x1 = v.second + dx[i];
            if (y1<0 || x1<0 || y1>=m || x1>=n) continue;
            if (visit[y1][x1]!=0) continue;
            if (img.ptr(y1)[x1] != 255 ) continue;
            ++numItems;
            visit[y1][x1] = component;
            q.push(make_pair(y1, x1));
        }
    }
    return numItems;
}
int extractDigit(Mat& digit) {
    vector<vector<int> > visit(digit.rows);
    for(int i = 0; i < digit.rows; ++i) {
        visit[i].resize(digit.cols, 0);
    }
    int component = 0;
    int mmax = 0;
    int t = 0;
    unordered_set<int> flyspeck;
    for(int y = 0; y < digit.rows; ++y) {
        for(int x = 0; x < digit.cols; ++x) {
            if (digit.ptr(y)[x] != 255 || visit[y][x] != 0) continue;
            int cnt = findConnectedComponent(y, x, digit, visit, ++component);
            if (cnt < CCA_THRESHOLD) {
                flyspeck.insert(component);
            } else {
                mmax = max(cnt, mmax);
            }
        }
    }
    if (mmax == 0) return 0;
    for(int y = 0; y < digit.rows; ++y) {
        for(int x = 0; x < digit.cols; ++x) {
            if (flyspeck.find(visit[y][x]) != flyspeck.end()) {
                digit.at<char>(y,x) = 0;
            }
        }
    }
    return mmax;
}

void findCellsUsingBfs(
    Mat& img, Mat& outerBox, 
    int numRow, 
    const std::string& inputFileName, 
    const std::string& outputFolder) 
 {
    /* Get the table from original image */
    Mat kernel = (Mat_<uchar>(3,3) << 0,1,0,1,1,1,0,1,0);
    Point2f src[4], dst[4];
    findFourCorners(outerBox, src);
    double maxLength = findDstCorners(src, dst);

    Mat original_img = imread(inputFileName, 0);
    Mat undistorted ;
    cv::warpPerspective(original_img, undistorted, cv::getPerspectiveTransform(src, dst), Size(maxLength, maxLength));
    printf("Value of maxLength = %lf\n", maxLength);
    int numCol = 0;
    vector<int> p = {
        1, 4, 3, 3, 1, 1,    
        1, 4, 3, 3, 1, 1};
    for(int i = 0; i < p.size(); ++i) {
        numCol += p[i];
    }
    double gapX = maxLength / numCol;
    double gapY = maxLength / numRow;

    Mat fullImageProcessedNumber;
    thresholdify(undistorted, fullImageProcessedNumber);
    bitwise_not(fullImageProcessedNumber, fullImageProcessedNumber);
    Mat fullImageProcessedBorder;
    preprocessing(undistorted,fullImageProcessedBorder, kernel);
    #if DEBUG
        imwrite(outputFolder + "/3.FullImageProcessedBorder.png", fullImageProcessedBorder);
        imwrite(outputFolder + "/3a.FullImageProcessedNumber.png", fullImageProcessedNumber);
    #endif
    vector<vector<int> > visit(fullImageProcessedBorder.rows);
    for(int i = 0; i < fullImageProcessedBorder.rows; ++i) {
        visit[i].resize(fullImageProcessedBorder.cols, 0);
    }
    int currentCnt = 0;
    for(int i = 0; i < numRow; ++i) {
        for(int j = 0; j < (i==0?1:numCol); ++j) {
            if (0 == j || 13==j) {
                continue;
            }
            Point p0, p1;
            p0.x = j * gapX;
            p0.y = i * gapY;
            p1.x = p0.x + gapX;
            p1.y = p0.y + gapY;
            p1.x = std::min(int(maxLength), p1.x);
            p1.y = std::min(int(maxLength), p1.y);
            string fileName = getFileName(i, j, numCol, outputFolder);
            cout <<"==============" << fileName << endl;
            // Get the largest black region, floodfill starting around the center square. 
            Mat digit;
            extractDigitSection(p0, p1, fullImageProcessedBorder, fullImageProcessedNumber, visit, currentCnt, digit);
            #if DEBUG
                imwrite(fileName + "3-ExtractTheDigitWithNoise.png", digit);
            #endif
            // Remove border of cells - this can lead to cell empty to be treated as non-empty
            Point cp1, cp2;
            getCellBorder(digit, 0.8, cp1, cp2);
            cout << "Cell border:"<<cp1<< " " << cp2 << endl;
            Mat section_border_removed = digit(Rect(cp1,cp2));
            #if DEBUG
                imwrite(fileName + "4-SectionWithBorderRemoved.png", section_border_removed);
            #endif
            int cnt = extractDigit(section_border_removed);
            cout << "Count of CCA:" << cnt << endl;
            if (cnt > CCA_THRESHOLD) {
                imwrite(fileName, section_border_removed);
            }
        }
    }
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

    printf("Preprocessing img\n");

    preprocessing(img,outerBox, kernel);
    imwrite(outputFolder + "/1.preprocessing_original_image.jpg", outerBox);

    printf("Find table blob");
    findTableBlob(outerBox, kernel);
    imwrite(outputFolder + "/2.findLargestBlob.jpg", outerBox);

    int numRows = 31;
    findCellsUsingBfs(img, outerBox, numRows, fileName, outputFolder);
}
