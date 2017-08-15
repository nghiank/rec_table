# Tesseract OCR
if(COMMAND pkg_check_modules)
  pkg_check_modules(Tesseract tesseract lept)
endif()
if(NOT Tesseract_FOUND)
  find_path(Tesseract_INCLUDE_DIR tesseract/baseapi.h
    HINTS
    /Users/nghiaround/homebrew/Cellar/tesseract/3.05.01/include)

  find_library(Tesseract_LIBRARY NAMES tesseract
    HINTS
    /Users/nghiaround/homebrew/Cellar/tesseract/3.05.01/lib)

  find_library(Lept_LIBRARY NAMES lept
    HINTS
    /Users/nghiaround/homebrew/Cellar/leptonica/1.74.4/lib)

  if(Tesseract_INCLUDE_DIR AND Tesseract_LIBRARY AND Lept_LIBRARY)
    set(Tesseract_INCLUDE_DIRS ${Tesseract_INCLUDE_DIR})
    set(Tesseract_LIBRARIES ${Tesseract_LIBRARY} ${Lept_LIBRARY})
    set(Tesseract_FOUND 1)
  endif()
endif()