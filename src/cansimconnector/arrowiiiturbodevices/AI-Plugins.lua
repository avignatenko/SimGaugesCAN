-- for stec-30 autopilot gauge

-- 0 - off, 1 - on
ap_engaged = create_dataref_table("ai/cockpit/gauges/ap/engaged", "Int")
ap_engaged[0] = 0

-- 0 - no warning, 1 - pitch up, 2 - pitch up more, 3 - pitch down, 4 - pitch down more
pitch_trim_warning = create_dataref_table("ai/cockpit/gauges/ap/pitch_trim_warning", "Int")
pitch_trim_warning[0] = 0
-- for CL control

-- NoChange = 0, Engage = 1, Disengage = 2
cl_engage = create_dataref_table("ai/cockpit/devices/cl_engage", "Int")
cl_engage[0] = 0