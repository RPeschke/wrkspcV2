function(ADD_RPATH TargetName)
 set_target_properties(${TargetName} PROPERTIES 
  BUILD_WITH_INSTALL_RPATH TRUE
  INSTALL_RPATH_USE_LINK_PATH TRUE
  INSTALL_RPATH "\$ORIGIN/../lib:${INSTALL_RPATH}"
  )



endfunction()