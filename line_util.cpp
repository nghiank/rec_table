#include "line_util.hpp"
#include "debug_util.hpp"
using namespace std;
using namespace cv;

void mergeRelatedLines(vector<Vec2f> *lines, Mat &img)
{
    vector<Vec2f>::iterator current;
    for(current=lines->begin();current!=lines->end();current++) {
        if((*current)[0]==0 && (*current)[1]==-100) {
            //printf("Skip line\n");
            continue;
        }
        float p1 = (*current)[0];
        float theta1 = (*current)[1];
        Point pt1current, pt2current;
        if(theta1>CV_PI*45/180 && theta1<CV_PI*135/180) {
            pt1current.x=0;
            
            pt1current.y = p1/sin(theta1);
            
            pt2current.x=img.size().width;
            pt2current.y=-pt2current.x/tan(theta1) + p1/sin(theta1);
        }
        else {
            pt1current.y=0;
            
            pt1current.x=p1/cos(theta1);
            
            pt2current.y=img.size().height;
            pt2current.x=-pt2current.y/tan(theta1) + p1/cos(theta1);
            
        }
        vector<Vec2f>::iterator    pos;
        for(pos=lines->begin();pos!=lines->end();pos++) {
            if(*current==*pos) continue;
        
            if(fabs((*pos)[0]-(*current)[0])<20 && fabs((*pos)[1]-(*current)[1])<CV_PI*10/180) {
                float p = (*pos)[0];
                float theta = (*pos)[1];
                Point pt1, pt2;
                if((*pos)[1]>CV_PI*45/180 && (*pos)[1]<CV_PI*135/180) {
                    pt1.x=0;
                    pt1.y = p/sin(theta);
                    pt2.x=img.size().width;
                    pt2.y=-pt2.x/tan(theta) + p/sin(theta);
                }
                else {
                    pt1.y=0;
                    pt1.x=p/cos(theta);
                    pt2.y=img.size().height;
                    pt2.x=-pt2.y/tan(theta) + p/cos(theta);
                }
                if(((double)(pt1.x-pt1current.x)*(pt1.x-pt1current.x) + (pt1.y-pt1current.y)*(pt1.y-pt1current.y)<64*64) &&
                   ((double)(pt2.x-pt2current.x)*(pt2.x-pt2current.x) + (pt2.y-pt2current.y)*(pt2.y-pt2current.y)<64*64))
                {
                    // Merge the two
                    (*current)[0] = ((*current)[0]+(*pos)[0])/2;
                
                    (*current)[1] = ((*current)[1]+(*pos)[1])/2;
                
                    (*pos)[0]=0;
                    (*pos)[1]=-100;
                }
            }
        }
    }
}

double findExtremeLines(vector<Vec2f>& lines, Mat& img, Point2f src[4], Point2f dst[4]) {
    printf("Number of extreme lines %lu\n", lines.size());
    // Now detect the lines on extremes
    Vec2f topEdge = Vec2f(1000,1000);    double topYIntercept=100000, topXIntercept=0;
    Vec2f bottomEdge = Vec2f(-1000,-1000);        double bottomYIntercept=0, bottomXIntercept=0;
    Vec2f leftEdge = Vec2f(1000,1000);    double leftXIntercept=100000, leftYIntercept=0;
    Vec2f rightEdge = Vec2f(-1000,-1000);        double rightXIntercept=0, rightYIntercept=0;
    for(int i=0;i<lines.size();i++) {
        Vec2f current = lines[i];
        float p=current[0];
        float theta=current[1];
        if(p==0 && theta==-100)
            continue;
        
        double xIntercept;
        // Equations: y = (-cos(theta) / sin(theta) ) * x  + r / sin(theta);
        xIntercept = p/cos(theta);
        if(theta>CV_PI*80/180 && theta<CV_PI*100/180) {
            if(p<topEdge[0]) 
                topEdge = current;
            if(p>bottomEdge[0])
                bottomEdge = current;
        } else if(theta<CV_PI*10/180 || theta>CV_PI*170/180) {
            if(xIntercept>rightXIntercept) {
                rightEdge = current;
                rightXIntercept = xIntercept;
            } else if(xIntercept<=leftXIntercept) {
                leftEdge = current;
                leftXIntercept = xIntercept;
            }
        }
    }
    //drawLine(topEdge, img, CV_RGB(0,0,0));
    //drawLine(bottomEdge, img, CV_RGB(0,0,0));
    //drawLine(leftEdge, img, CV_RGB(0,0,0));
    //drawLine(rightEdge, img, CV_RGB(0,0,0));
    //imshow("original_image", img);
    //cv::waitKey();

    Point left1, left2, right1, right2, bottom1, bottom2, top1, top2;
    
    int height=img.size().height;
    int width=img.size().width;
    
    if(leftEdge[1]!=0) {
        left1.x=0;        left1.y=leftEdge[0]/sin(leftEdge[1]);
        left2.x=width;    left2.y=-left2.x/tan(leftEdge[1]) + left1.y;
    } else {
        left1.y=0;        left1.x=leftEdge[0]/cos(leftEdge[1]);
        left2.y=height;    left2.x=left1.x - height*tan(leftEdge[1]);
        
    }
    
    if(rightEdge[1]!=0) {
        right1.x=0;        right1.y=rightEdge[0]/sin(rightEdge[1]);
        right2.x=width;    right2.y=-right2.x/tan(rightEdge[1]) + right1.y;
    } else {
        right1.y=0;        right1.x=rightEdge[0]/cos(rightEdge[1]);
        right2.y=height;    right2.x=right1.x - height*tan(rightEdge[1]);
    }
    
    bottom1.x=0;    bottom1.y=bottomEdge[0]/sin(bottomEdge[1]);
    bottom2.x=width;bottom2.y=-bottom2.x/tan(bottomEdge[1]) + bottom1.y;
    top1.x=0;        top1.y=topEdge[0]/sin(topEdge[1]);
    top2.x=width;    top2.y=-top2.x/tan(topEdge[1]) + top1.y;
    
    // Next, we find the intersection of  these four lines
    double leftA = left2.y-left1.y;
    double leftB = left1.x-left2.x;
    
    double leftC = leftA*left1.x + leftB*left1.y;
    
    double rightA = right2.y-right1.y;
    double rightB = right1.x-right2.x;
    
    double rightC = rightA*right1.x + rightB*right1.y;
    
    double topA = top2.y-top1.y;
    double topB = top1.x-top2.x;
    
    double topC = topA*top1.x + topB*top1.y;
    
    double bottomA = bottom2.y-bottom1.y;
    double bottomB = bottom1.x-bottom2.x;
    
    double bottomC = bottomA*bottom1.x + bottomB*bottom1.y;
    
    // Intersection of left and top
    double detTopLeft = leftA*topB - leftB*topA;
    
    CvPoint ptTopLeft = cvPoint((topB*leftC - leftB*topC)/detTopLeft, (leftA*topC - topA*leftC)/detTopLeft);
    
    // Intersection of top and right
    double detTopRight = rightA*topB - rightB*topA;
    
    CvPoint ptTopRight = cvPoint((topB*rightC-rightB*topC)/detTopRight, (rightA*topC-topA*rightC)/detTopRight);
    
    // Intersection of right and bottom
    double detBottomRight = rightA*bottomB - rightB*bottomA;
    CvPoint ptBottomRight = cvPoint((bottomB*rightC-rightB*bottomC)/detBottomRight, (rightA*bottomC-bottomA*rightC)/detBottomRight);// Intersection of bottom and left
    double detBottomLeft = leftA*bottomB-leftB*bottomA;
    CvPoint ptBottomLeft = cvPoint((bottomB*leftC-leftB*bottomC)/detBottomLeft, (leftA*bottomC-bottomA*leftC)/detBottomLeft);
    
    int maxLength = (ptBottomLeft.x-ptBottomRight.x)*(ptBottomLeft.x-ptBottomRight.x) + (ptBottomLeft.y-ptBottomRight.y)*(ptBottomLeft.y-ptBottomRight.y);
    //printf("maxLength = %d\n", maxLength);
    int temp = (ptTopRight.x-ptBottomRight.x)*(ptTopRight.x-ptBottomRight.x) + (ptTopRight.y-ptBottomRight.y)*(ptTopRight.y-ptBottomRight.y);
    
    if(temp>maxLength) maxLength = temp;
    
    temp = (ptTopRight.x-ptTopLeft.x)*(ptTopRight.x-ptTopLeft.x) + (ptTopRight.y-ptTopLeft.y)*(ptTopRight.y-ptTopLeft.y);
    
    if(temp>maxLength) maxLength = temp;
    
    temp = (ptBottomLeft.x-ptTopLeft.x)*(ptBottomLeft.x-ptTopLeft.x) + (ptBottomLeft.y-ptTopLeft.y)*(ptBottomLeft.y-ptTopLeft.y);
    
    if(temp>maxLength) maxLength = temp;
    
    maxLength = sqrt((double)maxLength);
    src[0] = ptTopLeft;            dst[0] = Point2f(0,0);
    src[1] = ptTopRight;        dst[1] = Point2f(maxLength-1, 0);
    src[2] = ptBottomRight;        dst[2] = Point2f(maxLength-1, maxLength-1);
    src[3] = ptBottomLeft;        dst[3] = Point2f(0, maxLength-1);
    return maxLength;
}