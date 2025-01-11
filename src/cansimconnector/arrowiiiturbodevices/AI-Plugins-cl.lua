-- NoChange = 0, Engage = 1, Disengage = 2
cl_engage = create_dataref_table("ai/cockpit/devices/cl_engage", "Int")
cl_engage[0] = 0

function engage_cl(value)
    cl_engage[0] = value
  end

create_command("ai/cockpit/devices/cl_engage_on", "AI: Engage CL", "engage_cl(1)", "", "")
create_command("ai/cockpit/devices/cl_engage_off", "AI: Disengage CL", "engage_cl(2)", "", "")
