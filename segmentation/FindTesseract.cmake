# Tesseract OCR
if(COMMAND pkg_check_modules)
  pkg_check_modules(Tesseract tesseract lept)
endif()
if(NOT Tesseract_FOUND)
  find_path(Tesseract_INCLUDE_DIR tesseract/baseapi.h 
    PATHS ${TESSERACT_PREFIX}/include /usr/local/include NO_DEFAULT_PATH)
  find_library(Tesseract_LIBRARY NAMES tesseract 
    PATHS ${TESSERACT_PREFIX}/lib /usr/local/lib NO_DEFAULT_PATH)
  find_library(Lept_LIBRARY NAMES lept 
    PATHS ${LEPT_PREFIX}/lib /usr/local/lib NO_DEFAULT_PATH)

  if(Tesseract_INCLUDE_DIR AND Tesseract_LIBRARY AND Lept_LIBRARY)
    set(Tesseract_INCLUDE_DIRS ${Tesseract_INCLUDE_DIR})
    set(Tesseract_LIBRARIES ${Tesseract_LIBRARY} ${Lept_LIBRARY})
    set(Tesseract_FOUND 1)
  endif()
endif()