//
//  line_util.hpp
//  Line utility.
//
//  Created by Nghia Nguyen on 7/13/17.
//  Copyright © 2017 Nghia Nguyen. All rights reserved.
//

#ifndef line_util_hpp
#define line_util_hpp

#include <vector>
#include <opencv2/opencv.hpp>

void mergeRelatedLines(std::vector<cv::Vec2f> *lines, cv::Mat &img);

// Return the max length
double findExtremeLines(
    std::vector<cv::Vec2f>& lines, 
    cv::Mat& img, 
    cv::Point2f src[4], 
    cv::Point2f dst[4]);
#endif /* line_util_hpp */
