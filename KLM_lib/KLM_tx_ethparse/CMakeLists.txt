find_package(TCLAP  REQUIRED)
find_package(ROOT REQUIRED)

add_executable (tx_ethparse_RP src/tx_ethparse_RP.cpp)
ADD_RPATH(tx_ethparse_RP)

TARGET_LINK_LIBRARIES(tx_ethparse_RP CERN_ROOT KLM_lib  TCLAP)


INSTALL(TARGETS tx_ethparse_RP  
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)




add_executable (tx_ethparse1_ck src/tx_ethparse1_ck.cpp)
ADD_RPATH(tx_ethparse1_ck)

TARGET_LINK_LIBRARIES(tx_ethparse1_ck CERN_ROOT KLM_lib  )


INSTALL(TARGETS tx_ethparse1_ck  
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)