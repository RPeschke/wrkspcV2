


add_executable (tx_ethparse_RP src/tx_ethparse_RP.cpp)


TARGET_LINK_LIBRARIES(tx_ethparse_RP ${ROOT_LIBRARIES} KLM_lib )


INSTALL(TARGETS tx_ethparse_RP  
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)




add_executable (tx_ethparse1_ck src/tx_ethparse1_ck.cpp)


TARGET_LINK_LIBRARIES(tx_ethparse1_ck ${ROOT_LIBRARIES} KLM_lib )


INSTALL(TARGETS tx_ethparse1_ck  
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)