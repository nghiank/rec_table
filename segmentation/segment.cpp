#include <string>
#include <iostream>
#include "tesseract/baseapi.h"
#include <leptonica/allheaders.h>

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
    char *outText;
    tesseract::TessBaseAPI *api = new tesseract::TessBaseAPI();
    // Initialize tesseract-ocr with English, without specifying tessdata path
    if (api->Init(NULL, "eng")) {
        fprintf(stderr, "Could not initialize tesseract.\n");
        exit(1);
    }
    
    std::string input_file;
    std::cout << "Input file:";
    std::cin >> input_file;
    // Open input image with leptonica library
    Pix *image = pixRead(input_file.c_str());
    printf("Reading image...\n");
    api->SetImage(image);
    printf("Set Image\n");
    Boxa* boxes = api->GetComponentImages(tesseract::RIL_SYMBOL , true, NULL, NULL);
    if (boxes) {
        printf("Found %d textline image components.\n", boxes->n);
    }

    for (int i = 0; i < boxes->n; i++) {
        BOX* box = boxaGetBox(boxes, i, L_CLONE);
        api->SetRectangle(box->x, box->y, box->w, box->h);
        char* ocrResult = api->GetUTF8Text();
        int conf = api->MeanTextConf();
        fprintf(stdout, "Box[%d]: x=%d, y=%d, w=%d, h=%d, confidence: %d, text: %s\n",
                        i, box->x, box->y, box->w, box->h, conf, ocrResult);

        if (conf < 10) {
            continue;
        }
        Pix* image1 = pixClipRectangle(image, box, NULL);
        char buf[100];
        sprintf(buf, "file%d.png",i);
        printf("Writing to file %s\n", buf);
        pixWrite(buf, image1, IFF_PNG);    
    }
    // Destroy used object and release memory
    api->End();
    //delete [] outText;
    pixDestroy(&image);
    
    return 0;
}
