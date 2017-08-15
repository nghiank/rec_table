cmake_minimum_required(VERSION 3.2)
set (CMAKE_CXX_STANDARD 11)

project( Segmentation )
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR})
find_package( Tesseract REQUIRED )
include_directories( ${Tesseract_INCLUDE_DIRS} )
add_executable( segment segment.cpp)

message( STATUS "LIBS:"  ${Tesseract_LIBRARIES})
target_link_libraries( segment ${Tesseract_LIBRARIES} )