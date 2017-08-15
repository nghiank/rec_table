//
//  debug_util.hpp
//  Debugging utility.
//
//  Created by Nghia Nguyen on 7/13/17.
//  Copyright © 2017 Nghia Nguyen. All rights reserved.
//

#ifndef debug_util_hpp
#define debug_util_hpp

#include <opencv2/opencv.hpp>

void drawLine(cv::Vec2f line, cv::Mat &img, cv::Scalar rgb = CV_RGB(0,255,255));

#endif /* debug_utl_hpp */
