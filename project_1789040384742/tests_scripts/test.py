from autocar import AT  # noqa: E402
at = AT()
#print(at.power_discover())

# ps = at.power_open('ASRL13::INSTR')
print(at.usb_switch(port="COM14", usb_port=2))
# ps.set_output(on=False)
# at.sleep(5)
# ps.set_output(on=True)