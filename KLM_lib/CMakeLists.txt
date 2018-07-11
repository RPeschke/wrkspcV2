# project name
PROJECT(KLM_lib)

include(cmake/add_RPATH.cmake)

# project version
SET( ${PROJECT_NAME}_VERSION_MAJOR 1 )
SET( ${PROJECT_NAME}_VERSION_MINOR 0 )
SET( ${PROJECT_NAME}_VERSION_PATCH 0 )

 cmake_minimum_required(VERSION 3.5)
 
 SET(INSTALL_PREFIX "${PROJECT_SOURCE_DIR}" CACHE PATH "Prefix prepended to install directories")
SET(CMAKE_INSTALL_PREFIX "${INSTALL_PREFIX}" CACHE INTERNAL "Prefix prepended to install directories" FORCE)
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake/")


If(WIN32)
#add_compile_options("/std:c++latest")
else(WIN32)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
endif(WIN32)

ADD_SUBDIRECTORY(KLM_lib)
ADD_SUBDIRECTORY(KLM_test01)
ADD_SUBDIRECTORY(KLM_tx_ethparse)



