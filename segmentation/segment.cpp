/*
    Process the whole folder to break image into smaller images 
    which has individual characters.
    Sample: 
    make && 
    TESSDATA_PREFIX="/Users/nghiaround/homebrew/Cellar/tesseract/3.05.01/share/tessdata" ./segment 
    --n 139 
    --inputFolder /Users/nghiaround/Desktop/tmp 
    --outputFolder /Users/nghiaround/Desktop/out 
    --fileNamePrefix file
 */
#include <string>
#include <sstream>
#include <iostream>
#include "tesseract/baseapi.h"
#include <leptonica/allheaders.h>

using namespace std;
//Confident threshold
const int CONFIDENT_THRESHOLD = 10; 
const int MAX_FILE_LENGTH = 500;
const int MAX_WORD_LENGTH = 100;
const string INPUT_FOLDER_OPTION = "--inputFolder";
const string INPUT_FILE_PREFIX   = "--fileNamePrefix";
const string OUTPUT_FOLDER_OPTION = "--outputFolder";
const string NUMBER_FILES_OPTION = "--n";

char* getCmdOption(char ** begin, char ** end, const std::string & option) {
    char ** itr = std::find(begin, end, option);
    if (itr != end && ++itr != end) {
        return *itr;
    }
    return 0;
}

bool cmdOptionExists(char** begin, char** end, const std::string& option) {
    char ** itr =  std::find(begin, end, option);
    return itr != end && (++itr) != end;
}

bool segment(
    tesseract::TessBaseAPI *api,
    const std::string& input_file, 
    const string& fileNamePrefix,
    const string& outputFolder) {
    // Open input image with leptonica library
    Pix *image = pixRead(input_file.c_str());
    if (image == NULL) {
        return false;
    }
    api->SetImage(image);
    Boxa* boxes = api->GetComponentImages(tesseract::RIL_SYMBOL , true, NULL, NULL);
    if (boxes == NULL) {
        printf("Boxes is NULL for file %s\n", input_file.c_str());
        //TODO : report here
        return true;
    }
    printf("Found %d textline image components.\n", boxes->n);
    int cnt = 0;
    char buf[MAX_FILE_LENGTH];
    string fileName = fileNamePrefix + "%d.png";
    for (int i = 0; i < min(boxes->n, MAX_WORD_LENGTH) ; i++) {
        BOX* box = boxaGetBox(boxes, i, L_CLONE);
        api->SetRectangle(box->x, box->y, box->w, box->h);
        char* ocrResult = api->GetUTF8Text();
        int conf = api->MeanTextConf();
        /*
        fprintf(stdout, "Box[%d]: x=%d, y=%d, w=%d, h=%d, confidence: %d, text: %s\n",
                        i, box->x, box->y, box->w, box->h, conf, ocrResult);*/
        if (conf < CONFIDENT_THRESHOLD) {
            continue;
        }
        Pix* image1 = pixClipRectangle(image, box, NULL);
        sprintf(buf, fileName.c_str(), cnt++);
        pixWrite(buf, image1, IFF_PNG);    
    }
    pixDestroy(&image);
    return true;
}

int main(int argc, char** argv) {
    // Read argument inputs.
    if (!cmdOptionExists(argv, argv + argc, INPUT_FOLDER_OPTION)) {
        printf("Option %s missing\n", INPUT_FOLDER_OPTION.c_str());
        return 0;
    }
    string inputFolder = getCmdOption(argv, argv + argc, INPUT_FOLDER_OPTION);
    printf("Input folder:%s\n", inputFolder.c_str());

    if (!cmdOptionExists(argv, argv + argc, INPUT_FILE_PREFIX)) {
        printf("Option %s missing\n", INPUT_FILE_PREFIX.c_str());
        return 0;
    }
    string fileNamePrefix = getCmdOption(argv, argv + argc, INPUT_FILE_PREFIX);
    printf("File name prefix:%s\n", fileNamePrefix.c_str());

    if (!cmdOptionExists(argv, argv + argc, OUTPUT_FOLDER_OPTION)) {
        printf("Option %s missing\n", OUTPUT_FOLDER_OPTION.c_str());
        return 0;
    }
    string outputFolder = getCmdOption(argv, argv + argc, OUTPUT_FOLDER_OPTION);
    printf("Output folder:%s\n", outputFolder.c_str());

    if (!cmdOptionExists(argv, argv + argc, NUMBER_FILES_OPTION)) {
        printf("Option %s missing\n", NUMBER_FILES_OPTION.c_str());
        return 0;
    }
    string numFileStr = getCmdOption(argv, argv + argc, NUMBER_FILES_OPTION);
    stringstream s(numFileStr);
    int num_of_files = 0;
    s >> num_of_files;
    printf("Number of files to process:%d\n", num_of_files);

    // Init tesseract.
    char *outText;
    tesseract::TessBaseAPI *api = new tesseract::TessBaseAPI();
    // Initialize tesseract-ocr with English, without specifying tessdata path
    // Need to set env variable. For example:
    // TESSDATA_PREFIX="/Users/nghiaround/homebrew/Cellar/tesseract/3.05.01/share/tessdata"
    if (api->Init(NULL, "eng")) {
        fprintf(stderr, "Could not initialize tesseract.\n");
        exit(1);
    }
    string input_file_prefix = inputFolder + "/" + fileNamePrefix + "%d.png";
    string full_file_name_prefix = outputFolder + "/" + fileNamePrefix + "%d_sub_";
    char fileName[MAX_FILE_LENGTH];
    char outputFileName[MAX_FILE_LENGTH];
    for(int i = 0; i < num_of_files; ++i) {
        sprintf(fileName, input_file_prefix.c_str(), i);
        sprintf(outputFileName, full_file_name_prefix.c_str(), i);
        if (!segment(api, fileName, outputFileName, outputFolder)) {
            printf("Invalid input:%s\n", fileName);
            //TODO: exit here or report problems.
        }
    }
    // Destroy used object and release memory
    api->End();
    return 0;
}
