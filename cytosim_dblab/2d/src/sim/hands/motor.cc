// Cytosim was created by Francois Nedelec. Copyright 2007-2017 EMBL.

#include "motor.h"
#include "motor_prop.h"
#include "glossary.h"
#include "exceptions.h"
#include "iowrapper.h"
#include "simul.h"

//------------------------------------------------------------------------------

Motor::Motor(MotorProp const* p, HandMonitor* h)
: Hand(p,h), prop(p)
{
}


//------------------------------------------------------------------------------
void Motor::stepUnloaded()
{
    assert_true( attached() );
    
    // detach or move
    if ( testDetachment() )
        return;
    
    moveBy(prop->max_speed_dt);
}

//------------------------------------------------------------------------------

void Motor::stepLoaded(Vector const& force)
{
    assert_true( attached() );
//    bool movedAlready;
    // detachment depends on magnitude of force:
    if ( testKramersDetachment(force.norm()) )
//        bool movedAlready = 0;
        return;
    
    // the load is the projection of the force on the local direction of Fiber
    real load = force * dirFiber();
    
    // calculate load-dependent displacement:
    real dabs = prop->max_speed_dt + load * prop->var_speed_dt;

    // possibly limit the range of the speed:
    if ( prop->limit_speed )
    {
        if ( dabs < prop->min_dabs )
            dabs = prop->min_dabs;
        
        else if ( dabs > prop->max_dabs )
            dabs = prop->max_dabs;
    }
    // we want test whether the flag movedAlready is 1 or 0.
//    if (movedAlready==0)
    {moveBy(dabs);
    // create a flag that tells us whether we've moved or not.
//    bool movedAlready = 1;
    }
}



