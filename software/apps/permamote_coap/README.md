Permamote Openthread COAP App
=============================

This is the default app for Permamote. It utilizes
[OpenThread](https://github.com/openthread/openthread) to establish data
backhaul over COAP and services such as NTP and DNS.
This app periodically sends sensor data from the light color, temperature,
humidity and pressure sensors. The light and motion sensor send when
changes are detected. The acceleratometer is currently not implemented. Thread
configuration, Sensor periods/backoffs, and COAP, NTP, and DNS endpoints, are
defined in
[config.h](https://github.com/lab11/permamote/blob/master/software/apps/permamote_coap/config.h).

This application is configured to use Nordic's [background
bootloader](https://www.nordicsemi.com/DocLib/Content/SDK_Doc/nRF5_SDK/v15-2-0/lib_background_dfu).
Before flashing this app, make sure to generate keys, copy the keys, and flash the bootloader.

To generate keys, follow Nordic's process [here](https://www.nordicsemi.com/DocLib/Content/SDK_Doc/Thread_SDK/v2-0-0/thread_example_dfu).
```
nrfutil keys generate private.pem
nrfutil keys display --key pk --format code private.pem --out_file public.c
cp private.pem public.c ../bg_bootloader/.
```

Navigate to the
[`bg_bootloader`](https://github.com/lab11/permamote/tree/master/software/apps/bg_bootloader) directory and:
```
make flash
```

Next, generate the bootloader settings and flash this app, with an optional device ID:
```
make flash_first_dfu ID=C0:98:E5:11:00:XX
```

The app currently does not perform DFUs (the variable `trigger` is hardcoded as
`false`), as there are
[issues](https://devzone.nordicsemi.com/f/nordic-q-a/42396/thread-background-dfu---how-to-get-progress-in-app)
with the process and more work is needed to build a cloud-based infrastructure
for hosting device images.


