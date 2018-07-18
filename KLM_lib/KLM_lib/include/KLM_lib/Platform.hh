#ifndef INCLUDED_Platform
#define INCLUDED_Platform




#define  let const auto

#define  cauto const auto
#define  cautor const auto&

#ifdef WIN32

#ifdef __CINT__
#define DLLEXPORT
#else
#define DLLEXPORT __declspec(dllexport)
#endif
#else

#define DLLEXPORT
#endif


#include <memory>

#ifdef WIN32
#ifdef __CINT__
#define ROOTCLASS class 
#else
#define  ROOTCLASS class   __declspec(dllexport) 
#endif
#else

#define  ROOTCLASS class 

#endif

#ifdef WIN32
#ifdef __CINT__
#define ROOTFUNCTION 
#else
#define  ROOTFUNCTION  __declspec(dllexport) 
#endif
#else

#define  ROOTFUNCTION 

#endif


#endif // INCLUDED_Platform
