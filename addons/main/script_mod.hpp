// COMPONENT should be defined in the script_component.hpp and included BEFORE this hpp

#define MAINPREFIX z
#define PREFIX cavaux

#include "script_version.hpp"

#define VERSION     MAJOR.MINOR
#define VERSION_STR MAJOR.MINOR.PATCHLVL.BUILD
#define VERSION_AR  MAJOR,MINOR,PATCHLVL,BUILD

// MINIMAL required version for the Mod. Components can specify others..
#define REQUIRED_VERSION 2.02
#define REQUIRED_CBA_VERSION {3,16,0}

#ifdef COMPONENT_BEAUTIFIED
    #define COMPONENT_NAME QUOTE(7th Cavalry Auxiliary Addon - COMPONENT_BEAUTIFIED)
#else
    #define COMPONENT_NAME QUOTE(PREFIX - COMPONENT)
#endif
