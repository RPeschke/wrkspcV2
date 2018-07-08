
# print system information
#
# if you are building in-source, this is the same as CMAKE_SOURCE_DIR, otherwise 
# this is the top level directory of your build tree 
MESSAGE( STATUS "Searching for TCLAP:" )
find_path(TCLAP_INCLUDE_DIR_dummy CmdLine.h  HINTS ${PROJECT_SOURCE_DIR}/extern/tclap/include/tclap/)

#MESSAGE( STATUS "TCLAP_INCLUDE_DIR_dummy: ${TCLAP_INCLUDE_DIR_dummy}" )


string(REPLACE "/include/tclap" "/include" TCLAP_INCLUDE_DIR ${TCLAP_INCLUDE_DIR_dummy})
#MESSAGE( STATUS "TCLAP_INCLUDE_DIR: ${TCLAP_INCLUDE_DIR}" )



#MESSAGE( STATUS "TCLAP_INCLUDE_DIR: ${TCLAP_INCLUDE_DIR}" )

include(FindPackageHandleStandardArgs)


find_package_handle_standard_args(TCLAP  DEFAULT_MSG TCLAP_INCLUDE_DIR)
mark_as_advanced(TCLAP_INCLUDE_DIR_dummy)
mark_as_advanced(TCLAP_INCLUDE_DIR)

add_library(TCLAP INTERFACE)
target_include_directories(TCLAP INTERFACE  ${TCLAP_INCLUDE_DIR})
target_compile_definitions(TCLAP INTERFACE USE_TCLAP)