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



#endif // INCLUDED_Platform
