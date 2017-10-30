//
//  preprocessing.hpp
//  Preprocessing the image.
//
//  Created by Nghia Nguyen on 7/13/17.
//  Copyright © 2017 Nghia Nguyen. All rights reserved.
//

#ifndef preprocessing_hpp
#define preprocessing_hpp

#include <opencv2/opencv.hpp>
#include "constants.hpp"

void thresholdify(cv::Mat& img, cv::Mat& out);
//Preprocessing the whole image before processing.
void preprocessing(
    cv::Mat& img, cv::Mat& outerBox, cv::Mat& kernel,
    int gaussian_size = 7, 
    int adaptiveThresholdSize = 11, 
    int adaptiveThresholdOffset = 5);

//Preprocessing only the cell.
void preprocessing_cell(cv::Mat& img, cv::Mat& outerBox, cv::Mat& kernel);

//Find largest connected blob in image.
cv::Point findLargestBlob(cv::Mat& outerBox, double gray_threshold = GRAY_THRESHOLD);

//Find the table blob.
void findTableBlob(cv::Mat& outerBox, cv::Mat& kernel);

#endif /* preprocessing_hpp */
