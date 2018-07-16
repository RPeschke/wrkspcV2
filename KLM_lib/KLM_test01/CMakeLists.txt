FIND_PACKAGE( ROOT REQUIRED)
file(GLOB src_files  "src/*.cpp" "src/*.cc" "src/*.cxx")






add_executable(KLM_test01 ${src_files})


TARGET_LINK_LIBRARIES(KLM_test01 KLM_lib CERN_ROOT )
target_include_directories(KLM_test01 PUBLIC include)
ADD_RPATH(KLM_test01)

INSTALL(TARGETS KLM_test01  
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)
