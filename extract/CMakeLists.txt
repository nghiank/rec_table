cmake_minimum_required(VERSION 2.8)
set (CMAKE_CXX_STANDARD 11)

project( ExtractWord )
find_package( OpenCV REQUIRED )
include_directories( ${OpenCV_INCLUDE_DIRS} )
add_executable( extract_cell extract_cell.cpp preprocessing.cpp debug_util.cpp line_util.cpp)
target_link_libraries( extract_cell ${OpenCV_LIBS} )