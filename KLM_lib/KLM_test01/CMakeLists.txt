FIND_PACKAGE( ROOT REQUIRED)
file(GLOB src_files  "src/*.cpp" "src/*.cc" "src/*.cxx")

include_directories(../Include ./inc )
include_directories(include ${ROOT_INCLUDE_DIR})
add_definitions(-DUSE_ROOT)



add_executable (KLM_test01 ${src_files})


TARGET_LINK_LIBRARIES(KLM_test01 ${ROOT_LIBRARIES} KLM_lib )


INSTALL(TARGETS KLM_test01  
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)
