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

//Preprocessing the whole image before processing.
void preprocessing(cv::Mat& img, cv::Mat& outerBox, cv::Mat& kernel);

//Preprocessing only the cell.
void preprocessing_cell(cv::Mat& img, cv::Mat& outerBox, cv::Mat& kernel);

//Find largest connected blob in image.
cv::Point findLargestBlob(cv::Mat& outerBox, double gray_threshold = 100);

//Find the table blob.
void findTableBlob(cv::Mat& outerBox, cv::Mat& kernel);

#endif /* preprocessing_hpp */
