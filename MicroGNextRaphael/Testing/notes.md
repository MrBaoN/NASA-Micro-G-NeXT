* add a low pass filter 1700 twice the bandwidth low pass filter 
* may not need a root raised cosine filter
* remove dc blocker: they are just for removing the dc offset on the waterfall
* wont need the dc blocker cause pluto takes care of it for you
* symbol sync for clock recovery and timing recovery, use that one instead, take out clock recovery, might need to take out costas loop
* symbol sync is the succesor to clock recovery
* configure to the number of samples per symbol, rn 1700, can configure to one 
* move the decimation to the symbol to the symbol sync, bring it down to 1 sample per symbol, figure out how to do that, decimate by 1700
* add a low pass filter before the rrc and after the sdr source
* you can remove the root raised cosine, 
* not sure what to do with a pwer squelch
* ideal match filter is convolve the square wave with an rcos filter so do that thing
* if you want to cheat you can even match it to this thing with the top and bottom of the square
* for match filtering you filter based on what your ideal pulse would look like
    * to do this slide thing over and multiply by it with your output 