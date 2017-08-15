//
//  constants.hpp
//  Constants.
//
//  Created by Nghia Nguyen on 7/13/17.
//  Copyright © 2017 Nghia Nguyen. All rights reserved.
//

#ifndef constants_hpp
#define constants_hpp

#include <opencv2/opencv.hpp>

cv::Mat KERNEL = (cv::Mat_<uchar>(3,3) << 0,1,0,1,1,1,0,1,0);

#endif /* constants_hpp */
